//! Export actual application traffic for language-neutral contract validation.
#[allow(dead_code)]
mod support;

use std::io::Write;

use kitu_demo_game::{
    arena::{self, script},
    build_arena_runtime, build_demo_runtime, DemoRuntime,
};
use kitu_osc_ir::{OscArg, OscBundle};
use kitu_transport::wire::WireBundle;

struct Trace(Option<std::io::BufWriter<std::fs::File>>);
impl Trace {
    fn bundles(&mut self, bundles: &[OscBundle]) {
        if let Some(writer) = &mut self.0 {
            for bundle in bundles {
                let wire = serde_json::to_value(WireBundle::try_from(bundle).unwrap()).unwrap();
                for message in wire["messages"].as_array().unwrap() {
                    serde_json::to_writer(&mut *writer, message).unwrap();
                    writeln!(writer).unwrap();
                }
            }
        }
    }

    fn tick(&mut self, runtime: &DemoRuntime, output: &[OscBundle]) {
        for input in runtime.committed_input_records() {
            self.bundles(&[input.bundle]);
        }
        self.bundles(output);
    }
}

#[test]
fn actual_arena_traffic_for_contract_validation() {
    let destination = std::env::var_os("KITU_ARENA_CONTRACT_TRACE");
    let mut trace = Trace(destination.map(|path| {
        let path = std::path::PathBuf::from(path);
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).unwrap();
        }
        // Verification evidence is never silently overwritten.
        std::io::BufWriter::new(std::fs::File::create_new(path).unwrap())
    }));
    let mut runtime = build_arena_runtime().unwrap();
    trace.bundles(&runtime.inspect_application());
    // Cover next-run management, including their exact reserved source identities.
    let content = arena::inspect_content(&runtime).unwrap().pending;
    arena::stage_content(&mut runtime, content.clone(), 1).unwrap();
    arena::stage_script(&mut runtime, script::default_script().unwrap(), 1).unwrap();
    arena::stage_timeline(
        &mut runtime,
        arena::presentation::default_timeline().unwrap(),
        1,
    )
    .unwrap();
    for (index, (address, args)) in [
        ("start", vec![]),
        ("inventory", vec![]),
        ("unequip", vec![OscArg::Int(1), OscArg::Int(0)]),
        ("discard", vec![OscArg::Int(1), OscArg::Int(0)]),
        ("close", vec![]),
        ("disconnect", vec![]),
        ("resume", vec![]),
        ("use", vec![OscArg::Int(2)]),
    ]
    .into_iter()
    .enumerate()
    {
        support::send(
            &mut runtime,
            "contract:commands",
            index as u64 + 1,
            &format!("/input/arena/{address}"),
            args,
        );
        runtime.tick_once().unwrap();
        let output = runtime.drain_output_buffer();
        trace.tick(&runtime, &output);
    }
    // Exercise actual consumable use; the frozen stock run never throws a grenade.
    let mut consumables = build_arena_runtime().unwrap();
    support::send(
        &mut consumables,
        "consumables",
        1,
        "/input/arena/start",
        vec![],
    );
    let length = 58.0_f32.sqrt();
    support::send(
        &mut consumables,
        "frames",
        1,
        "/input/arena/frame",
        vec![
            OscArg::Float(-3.0 / length),
            OscArg::Float(7.0 / length),
            OscArg::Bool(true),
            OscArg::Float(0.0),
            OscArg::Float(5.0),
            OscArg::Bool(false),
            OscArg::Bool(false),
        ],
    );
    for _ in 0..75 {
        consumables.tick_once().unwrap();
        let output = consumables.drain_output_buffer();
        trace.tick(&consumables, &output);
    }
    for (id, address, args) in [
        (2, "chest", vec![]),
        (3, "take", vec![OscArg::Int(9), OscArg::Int(0)]),
        (
            4,
            "equip",
            vec![OscArg::Int(9), OscArg::Int(0), OscArg::Int(2)],
        ),
        (5, "close", vec![]),
        (6, "use", vec![OscArg::Int(2)]),
    ] {
        if address == "use" {
            // Closing an overlay clears held controls, including aim validity.
            support::send(
                &mut consumables,
                "frames",
                2,
                "/input/arena/frame",
                vec![
                    OscArg::Float(0.0),
                    OscArg::Float(0.0),
                    OscArg::Bool(true),
                    OscArg::Float(0.0),
                    OscArg::Float(5.0),
                    OscArg::Bool(false),
                    OscArg::Bool(false),
                ],
            );
        }
        support::send(
            &mut consumables,
            "consumables",
            id,
            &format!("/input/arena/{address}"),
            args,
        );
    }
    for _ in 0..60 {
        consumables.tick_once().unwrap();
        let output = consumables.drain_output_buffer();
        trace.tick(&consumables, &output);
    }
    // The oracle still checks all recorded state checkpoints and command outcomes.
    let mut fault_runtime = build_demo_runtime().unwrap();
    let faulty = script::ScriptVersion::from_source(&script::DEFAULT_SOURCE.replace(
        "fn boss(input) {",
        "fn boss(input) { if input.floor == 10 { throw \"contract fault\"; }",
    ))
    .unwrap();
    arena::install_with_versions(&mut fault_runtime, content, faulty).unwrap();
    let mut saw_fault = false;
    for scenario in ["preparation", "stock-eleven-death-retry"] {
        support::replay_reference_observing_ticks(
            scenario,
            usize::MAX,
            |_| {},
            |reference, output| {
                trace.tick(reference, output);
                if scenario == "stock-eleven-death-retry" && !saw_fault {
                    for input in reference.committed_input_records() {
                        fault_runtime
                            .try_enqueue_input(input.bundle, input.metadata)
                            .unwrap();
                    }
                    fault_runtime.tick_once().unwrap();
                    let outputs = fault_runtime.drain_output_buffer();
                    trace.tick(&fault_runtime, &outputs);
                    saw_fault = arena::inspect_script(&fault_runtime)
                        .unwrap()
                        .fault
                        .is_some();
                }
            },
        );
    }
    assert!(
        saw_fault,
        "real boss path must exercise the late-fault contract"
    );
    if let Some(mut writer) = trace.0 {
        writer.flush().unwrap();
    }
}
