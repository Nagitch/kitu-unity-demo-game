# Arena v1 message semantics

Hand-authored source for the generated event reference. Edit these sections, then regenerate.

## /input/arena/start

Accepted in Opening or Results. Increments the run number, adopts pending content/script/timeline, resets run state and enters Preparing. Emits run, source snapshots, phase (when changed), and the receipt. The same tick may advance gameplay.

## /input/arena/menu

Clears the run and presentation cues; emits phase only if the phase changed. Retains the last run/source metadata. Do not expect per-object despawn events for every object cleared by this reset.

## /input/arena/pause

Accepted outside Opening/Results. Sets the pause overlay and clears held controls and queued use intents. This changes the state snapshot, not the game phase event.

## /input/arena/resume

Accepted only for a paused active run without a script fault. Clears the overlay and resets held/queued controls. Fresh player input is required.

## /input/arena/disconnect

Host-only command; not admitted through the Arena socket or external operator shell. Pauses an active run and clears held/queued controls. Reconnection does not automatically resume.

## /input/arena/inventory

Accepted only in Preparing/Cleared with no overlay. Opens the inventory overlay and freezes gameplay.

## /input/arena/chest

Accepted only in a safe phase with no overlay, an available chest and player distance at most 2 world units. Out-of-range attempts produce a rejected command receipt.

## /input/arena/close

Accepted only for the inventory/chest overlay. Clears held/queued controls; Unity requires button release before new gameplay actions.

## /input/arena/frame

Latest continuous input, not a discrete attack request. Movement is clamped to unit length by simulation. Aim is an absolute point on the X/Z plane. Ordinary accepted frames have no command receipt. Frames received during an overlay do not change controls; repeated/outdated frame IDs have special high-water handling. All coordinates must be finite.

## /input/arena/use

Slot 2 or 3 is eligible during an active unobscured run. An accepted command only queues intent. Repeated presses for one slot coalesce into one attempt on a gameplay step; transition steps discard queued intent. Consumption is reported separately by /ui/arena/use.

## /input/arena/take

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

## /input/arena/equip

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

## /input/arena/unequip

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

## /input/arena/discard

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

## /input/arena/upgrade

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

## /input/arena/config

Authorized producers: `host:arena-content` and `host:arena-content-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

## /input/arena/script

Authorized producers: `host:arena-script` and `host:arena-script-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

## /input/arena/timeline

Authorized producers: `host:arena-timeline` and `host:arena-timeline-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

## /game/arena/run

Emitted once per accepted start/retry before that start's phase event and receipt. Captures the full adopted content, script and timeline. Use run to reset presentation identity; do not use this as a per-tick state update.

## /game/arena/attack

Emitted only when an attack actually executes, not on every held button frame. Player weapon kind is an ItemKind number; enemy attack kind is an EnemyKind number; grenade and boss_burst are strings. itemId, direction and target are variant-specific. A boss burst emits one attack followed by eight projectile spawns. attackId is not a universal actor ID or a one-to-one identifier for every burst projectile. Use origin for one-shot effects and correlate with the actor/state where needed.

## /game/arena/damage

Enemy damage is aggregated per target for the gameplay step, in first-hit order, with all contributing attackIds. Enemy deaths are processed next, then incoming player damage. damage is attempted damage before shield absorption and HP clamping; absorbed is shield charge consumed, not HP loss. No impact position, sourceId or damage-type field exists in v1. Obtain position from the displayed actor before despawn or use the separate hit effect.

## /game/arena/death

Enemy deaths are emitted in reverse enemy-list order and immediately followed by enemy despawn. Player death uses entityId 0 and string kind player; enemy kind is numeric. Player death precedes Results and the result event, and prevents floor-clear rewards. No position is included; preserve the last displayed transform for the death animation.

## /game/arena/inventory

Transfer/upgrade events carry tick, input sequence, source and messageId, but no order field. Consumable events carry tick/order and no single input identity because use intents coalesce. index/slot can be unused zero placeholders for some transfer operations. inventory is the complete post-operation state. Rejected and duplicate commands never repeat the mutation notification.

## /game/arena/phase

Emitted for lifecycle phase changes and progression: Opening=0, Preparing=1, Transition=2, Combat=3, Cleared=4, Results=5. Pause/inventory/chest are overlays and do not emit this event. Floor enemies spawn before Combat. Last-enemy clear emits Cleared before transient cleanup and any boss reward; portal entry emits Transition.

## /game/arena/reward

Emitted once after a living player clears a floor divisible by five. Contains full healing and generated chest item IDs plus complete inventory. Ordinary floor clears emit phase but no reward event.

## /game/arena/result

Emitted after player death, the Results phase change and transient cleanup. The nested result is captured at death and remains immutable for that completed run. Use it for result animation; use the state snapshot to restore the screen after reconnect/seek.

## /game/arena/script-fault

A late script failure consumes one management tick, emits this fault and the script snapshot, and pauses without partially applying gameplay. No order or run field is present in this payload. Resume cannot bypass it; a new run clears the fault. Treat diagnostic text as display text, not a stable branching key.

## /render/arena/spawn

Contains the new entityId, string kind and the complete initial actor state. Actor-state keys are PascalCase, unlike most Arena payloads. Effect kinds are Slash=0, Explosion=1, Hit=2. Spawned objects may also disappear within the same tick; do not rely solely on final state differences for one-shot visuals.

## /render/arena/despawn

Emitted on enemy death, projectile expiry/impact, grenade detonation, effect timeout and transient cleanup. No reason or position is included. Despawn does not necessarily mean death or impact. Lifecycle resets can instead replace the whole state; reconcile against snapshots.

## /ui/arena/command

Reports acceptance, duplication and reason code. id is the producer message ID; sequence is Runtime input sequence. tick is the current response tick; appliedTick preserves the original application tick for duplicates, or -1 on ID conflict. A successful use receipt does not guarantee consumption. Unknown/malformed commands fail admission rather than emitting an unknown_command receipt. Do not trigger gameplay effects again for duplicates.

## /ui/arena/use

Emitted once per coalesced attempt on a gameplay step. consumed=true with code ok follows the inventory consumption event. Empty slots, automatic shields, full HP and invalid grenade aim do not consume an item. Successful grenade use then emits attack/spawn; medkit use has no dedicated heal event.

## /ui/arena/timeline/event

kind is start, event or stop. Applied events preserve trackIndex/eventIndex and an exact typed OSC bundle (including empty bundles). These audit records follow original game events and precede the final state/presentation pair. Their message order fields are indices in the complete output bundle, not a separate timeline counter. Nested messages are authored cue assignments, not separately broadcast top-level events.

## /ui/arena/state

Emitted at the end of every management tick and on inspection, even when paused. Contains current actor transforms, inventory, overlays and result. There is no separate Arena transform event. Reconcile the whole state on lifecycle changes and snapshots; publish together with presentation only when tick and simulation-step counts match.

## /render/arena/presentation

Emitted after state at each tick and on inspection. Includes live boss cues and the optional floor fade. Render radius/intensity/opacity directly; Unity frames must not advance cue offsets. Pause, overlays and faults freeze simulation steps while management ticks continue. Seek may move time backwards.

## /ui/arena/content

Emitted on inspection and successful start/content stage, not every tick. active is null before a run and retained after returning to the menu. Pending content is adopted only on start/retry.

## /ui/arena/script

Emitted on inspection, start/script stage and late faults. Includes active/pending detached source and nullable fault. Staging a repaired script does not repair the current run; start a new run.

## /ui/arena/timeline

Emitted on inspection and successful start/timeline stage. Same-tick updates are coalesced into a complete snapshot after presentation has advanced. Includes detached TSQ1 bytes and current presentation; not a command to independently play those bytes in Unity.

## /render/arena/cue/boss

Allowed only inside boss-telegraph clips. Radius is 0.25..8 world units; intensity is 0..1. Every clip initializes values at offset zero. An actual boss phase 0→1 creates the cue; its last assignment persists until the boss leaves telegraph or dies. Runtime publishes the resulting presentation snapshot.

## /render/arena/cue/floor

Allowed only inside floor-transition clips. Opacity is 0..1; initialize at offset zero and end with opacity zero. Entering Transition starts the cue; it may outlive the transition into the next floor. Its last event removes it. Unity draws the fade behind the HUD.
