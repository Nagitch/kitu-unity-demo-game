# Arena OSC event reference

This is the human-readable, normative Arena v1 application-message contract.
Start with the category tables below and follow an address to its arguments,
payload variants, emission semantics and Unity integration guidance. GitHub and
Markdown editors can display this file without running any tooling.

Browse: [game events](#game-events) · [object lifecycle](#object-lifecycle) ·
[state snapshots](#state-snapshots) · [input commands](#input-commands) ·
[shared rendering rules](#shared-timing-identity-and-rendering-rules) ·
[updating the contract](#ownership-and-changes).

<!-- BEGIN GENERATED ARENA CONTRACT -->

This reference covers **39 OSC addresses**. Tables and examples are generated; behavioral notes are authored in [semantics.md](../contracts/arena-v1/semantics.md).

## Input commands

| Address | Meaning |
| --- | --- |
| [`/input/arena/start`](#input-arena-start) | Start or retry a run |
| [`/input/arena/menu`](#input-arena-menu) | Return to opening |
| [`/input/arena/pause`](#input-arena-pause) | Pause an active run |
| [`/input/arena/resume`](#input-arena-resume) | Resume a paused run |
| [`/input/arena/disconnect`](#input-arena-disconnect) | Pause after controller loss |
| [`/input/arena/inventory`](#input-arena-inventory) | Open inventory |
| [`/input/arena/chest`](#input-arena-chest) | Open chest |
| [`/input/arena/close`](#input-arena-close) | Close inventory or chest |
| [`/input/arena/frame`](#input-arena-frame) | Latest movement, aim and held-fire state |
| [`/input/arena/use`](#input-arena-use) | Queue one consumable press |
| [`/input/arena/take`](#input-arena-take) | Take or swap a chest item |
| [`/input/arena/equip`](#input-arena-equip) | Equip a backpack item |
| [`/input/arena/unequip`](#input-arena-unequip) | Return equipment to backpack |
| [`/input/arena/discard`](#input-arena-discard) | Discard a backpack item |
| [`/input/arena/upgrade`](#input-arena-upgrade) | Consume a permanent upgrade |

## Management inputs

| Address | Meaning |
| --- | --- |
| [`/input/arena/config`](#input-arena-config) | Stage next-run config |
| [`/input/arena/script`](#input-arena-script) | Stage next-run script |
| [`/input/arena/timeline`](#input-arena-timeline) | Stage next-run timeline |

## Game events

| Address | Meaning |
| --- | --- |
| [`/game/arena/run`](#game-arena-run) | Run started |
| [`/game/arena/attack`](#game-arena-attack) | Attack executed |
| [`/game/arena/damage`](#game-arena-damage) | Damage applied |
| [`/game/arena/death`](#game-arena-death) | Entity died |
| [`/game/arena/inventory`](#game-arena-inventory) | Inventory changed |
| [`/game/arena/phase`](#game-arena-phase) | Game phase changed |
| [`/game/arena/reward`](#game-arena-reward) | Boss-floor reward granted |
| [`/game/arena/result`](#game-arena-result) | Run result finalized |
| [`/game/arena/script-fault`](#game-arena-script-fault) | Boss script failed |

## Object lifecycle

| Address | Meaning |
| --- | --- |
| [`/render/arena/spawn`](#render-arena-spawn) | Spawn an enemy, projectile, grenade or effect |
| [`/render/arena/despawn`](#render-arena-despawn) | Remove an actor or effect |

## Receipts and timeline events

| Address | Meaning |
| --- | --- |
| [`/ui/arena/command`](#ui-arena-command) | Discrete command receipt |
| [`/ui/arena/use`](#ui-arena-use) | Consumable attempt result |
| [`/ui/arena/timeline/event`](#ui-arena-timeline-event) | Presentation cue audit |

## State snapshots

| Address | Meaning |
| --- | --- |
| [`/ui/arena/state`](#ui-arena-state) | Complete gameplay state |
| [`/render/arena/presentation`](#render-arena-presentation) | Complete timeline presentation state |
| [`/ui/arena/content`](#ui-arena-content) | Active and pending game content |
| [`/ui/arena/script`](#ui-arena-script) | Active and pending boss script |
| [`/ui/arena/timeline`](#ui-arena-timeline) | Active and pending timeline sources |

## TSQ1 clip messages

| Address | Meaning |
| --- | --- |
| [`/render/arena/cue/boss`](#render-arena-cue-boss) | Assign boss warning radius and intensity |
| [`/render/arena/cue/floor`](#render-arena-cue-floor) | Assign floor fade opacity |

## Message details

<a id="input-arena-start"></a>

### `/input/arena/start`

Start or retry a run.

Accepted in Opening or Results. Increments the run number, adopts pending content/script/timeline, resets run state and enters Preparing. Emits run, source snapshots, phase (when changed), and the receipt. The same tick may advance gameplay.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-start-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/start",
  "args": []
}
```

<a id="input-arena-menu"></a>

### `/input/arena/menu`

Return to opening.

Clears the run and presentation cues; emits phase only if the phase changed. Retains the last run/source metadata. Do not expect per-object despawn events for every object cleared by this reset.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-menu-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/menu",
  "args": []
}
```

<a id="input-arena-pause"></a>

### `/input/arena/pause`

Pause an active run.

Accepted outside Opening/Results. Sets the pause overlay and clears held controls and queued use intents. This changes the state snapshot, not the game phase event.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-pause-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/pause",
  "args": []
}
```

<a id="input-arena-resume"></a>

### `/input/arena/resume`

Resume a paused run.

Accepted only for a paused active run without a script fault. Clears the overlay and resets held/queued controls. Fresh player input is required.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-resume-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/resume",
  "args": []
}
```

<a id="input-arena-disconnect"></a>

### `/input/arena/disconnect`

Pause after controller loss.

Host-only command; not admitted through the Arena socket or external operator shell. Pauses an active run and clears held/queued controls. Reconnection does not automatically resume.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-disconnect-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/disconnect",
  "args": []
}
```

<a id="input-arena-inventory"></a>

### `/input/arena/inventory`

Open inventory.

Accepted only in Preparing/Cleared with no overlay. Opens the inventory overlay and freezes gameplay.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-inventory-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/inventory",
  "args": []
}
```

<a id="input-arena-chest"></a>

### `/input/arena/chest`

Open chest.

Accepted only in a safe phase with no overlay, an available chest and player distance at most 2 world units. Out-of-range attempts produce a rejected command receipt.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-chest-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/chest",
  "args": []
}
```

<a id="input-arena-close"></a>

### `/input/arena/close`

Close inventory or chest.

Accepted only for the inventory/chest overlay. Clears held/queued controls; Unity requires button release before new gameplay actions.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| — | — | — | No arguments; an empty args array is required. |

Examples: [input-arena-close-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/close",
  "args": []
}
```

<a id="input-arena-frame"></a>

### `/input/arena/frame`

Latest movement, aim and held-fire state.

Latest continuous input, not a discrete attack request. Movement is clamped to unit length by simulation. Aim is an absolute point on the X/Z plane. Ordinary accepted frames have no command receipt. Frames received during an overlay do not change controls; repeated/outdated frame IDs have special high-water handling. All coordinates must be finite.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `move_x` | `float` | World X movement axis. |
| 1 | `move_z` | `float` | World Z movement axis. |
| 2 | `has_aim` | `bool` | Whether aim coordinates are valid. |
| 3 | `aim_x` | `float` | World X target position. |
| 4 | `aim_z` | `float` | World Z target position. |
| 5 | `fire_a` | `bool` | Weapon A held. |
| 6 | `fire_b` | `bool` | Weapon B held. |

Examples: [input-arena-frame-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/frame",
  "args": [
    {
      "type": "float",
      "value": -0.39391928911209106
    },
    {
      "type": "float",
      "value": 0.9191450476646423
    },
    {
      "type": "bool",
      "value": true
    },
    {
      "type": "float",
      "value": 0.0
    },
    {
      "type": "float",
      "value": 5.0
    },
    {
      "type": "bool",
      "value": false
    },
    {
      "type": "bool",
      "value": false
    }
  ]
}
```

<a id="input-arena-use"></a>

### `/input/arena/use`

Queue one consumable press.

Slot 2 or 3 is eligible during an active unobscured run. An accepted command only queues intent. Repeated presses for one slot coalesce into one attempt on a gameplay step; transition steps discard queued intent. Consumption is reported separately by /ui/arena/use.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `slot` | `int` | ItemA=2 or ItemB=3; other i32 values are structurally valid but rejected by game rules. |

Examples: [input-arena-use-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/use",
  "args": [
    {
      "type": "int",
      "value": 2
    }
  ]
}
```

<a id="input-arena-take"></a>

### `/input/arena/take`

Take or swap a chest item.

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `item_id` | `int` | Expected current item ID; stale IDs are rejected. |
| 1 | `backpack_index` | `int` | Backpack position 0..2. |

Examples: [input-arena-take-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/take",
  "args": [
    {
      "type": "int",
      "value": 9
    },
    {
      "type": "int",
      "value": 0
    }
  ]
}
```

<a id="input-arena-equip"></a>

### `/input/arena/equip`

Equip a backpack item.

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `item_id` | `int` | Expected current item ID; stale IDs are rejected. |
| 1 | `backpack_index` | `int` | Backpack position 0..2. |
| 2 | `equipment_slot` | `int` | WeaponA=0, WeaponB=1, ItemA=2, ItemB=3. |

Examples: [input-arena-equip-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/equip",
  "args": [
    {
      "type": "int",
      "value": 9
    },
    {
      "type": "int",
      "value": 0
    },
    {
      "type": "int",
      "value": 2
    }
  ]
}
```

<a id="input-arena-unequip"></a>

### `/input/arena/unequip`

Return equipment to backpack.

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `item_id` | `int` | Expected current item ID; stale IDs are rejected. |
| 1 | `equipment_slot` | `int` | WeaponA=0, WeaponB=1, ItemA=2, ItemB=3. |

Examples: [input-arena-unequip-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/unequip",
  "args": [
    {
      "type": "int",
      "value": 1
    },
    {
      "type": "int",
      "value": 0
    }
  ]
}
```

<a id="input-arena-discard"></a>

### `/input/arena/discard`

Discard a backpack item.

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `item_id` | `int` | Expected current item ID; stale IDs are rejected. |
| 1 | `backpack_index` | `int` | Backpack position 0..2. |

Examples: [input-arena-discard-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/discard",
  "args": [
    {
      "type": "int",
      "value": 1
    },
    {
      "type": "int",
      "value": 0
    }
  ]
}
```

<a id="input-arena-upgrade"></a>

### `/input/arena/upgrade`

Consume a permanent upgrade.

Requires a safe phase and inventory/chest overlay; take additionally requires the chest overlay. Valid i32 arguments can still be rejected for stale identity, invalid target, slot capacity or item type. A successful mutation emits /game/arena/inventory before its receipt. Unequip requires a free backpack position.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `item_id` | `int` | Expected current item ID; stale IDs are rejected. |
| 1 | `backpack_index` | `int` | Backpack position 0..2. |

Examples: [input-arena-upgrade-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/input/arena/upgrade",
  "args": [
    {
      "type": "int",
      "value": 11
    },
    {
      "type": "int",
      "value": 0
    }
  ]
}
```

<a id="input-arena-config"></a>

### `/input/arena/config`

Stage next-run config.

Authorized producers: `host:arena-content` and `host:arena-content-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ContentVersion](#type-contentversion).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of the canonical evaluated values. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of legacy TMD bytes, or the complete ordered source provenance. |
| `tanuRevision` | `string` or `null` | no | Tanu API revision that evaluated the source. |
| `provenance` | [ContentProvenance](#type-contentprovenance) or `null` | no | Detached source kinds, digests and field origins; never filesystem paths. |
| `values` | [ArenaConfig](#type-arenaconfig) | yes | Complete values needed to reproduce gameplay without re-evaluating a file. |

Examples: [input-arena-config-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="input-arena-script"></a>

### `/input/arena/script`

Stage next-run script.

Authorized producers: `host:arena-script` and `host:arena-script-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ScriptVersion](#type-scriptversion).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of source plus the exact contract and execution policy identities. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of the UTF-8 source bytes. |
| `source` | `string` | yes | Detached source; never a filename or a reference to authoring state. |
| `contractVersion` | `1` | yes | Arena boss context/action schema. |
| `policyVersion` | `string` | yes | Generic sandbox policy identity. |
| `rhaiVersion` | `string` | yes | Exact Rhai dependency version. |

Examples: [input-arena-script-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "hash": "1972fdeaaed2d2e6ff349409087a20440683b1aa90f0199c2f7e0c7a22564025",
  "sourceSha256": "cc75bd728a7fcddaf067e13bf330e650b57c26530bc805ed4683e5f8bb711af1",
  "source": "// Arena boss contract 1. Context is a copied JSON value; actions have no side effects.\n// Rust advances the f32 phase timer and applies radial shots in the reference order.\nfn boss(input) {\n    if input.phase == 0 {\n        if input.timerExpired {\n            return #{action: \"telegraph\", duration: 0.8};\n        }\n        return #{action: \"pursue\", duration: 0.0};\n    }\n    if input.phase == 1 {\n        if input.timerExpired {\n            return #{action: \"burst\", duration: 1.0};\n        }\n        return #{action: \"wait\", duration: 0.0};\n    }\n    if input.timerExpired {\n        return #{action: \"recover\", duration: 3.0};\n    }\n    #{action: \"wait\", duration: 0.0}\n}\n",
  "contractVersion": 1,
  "policyVersion": "kitu-rhai-json-v1",
  "rhaiVersion": "1.26.0"
}
```

<a id="input-arena-timeline"></a>

### `/input/arena/timeline`

Stage next-run timeline.

Authorized producers: `host:arena-timeline` and `host:arena-timeline-admin`.

Restricted to the corresponding host-owned producer identity (including its Admin variant); not an ordinary player command. Accepts one detached JSON version, bounded to 128 KiB. Updates pending values, never the active run. Hashes, semantic constraints and script/TSQ1 validity are checked by the existing application validators. Changes take effect on the next successful start/retry.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [TimelineVersion](#type-timelineversion).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of contract, tick rate and ordered clip identities. |
| `contractVersion` | `1` | yes | Arena presentation schema. |
| `tickRate` | `60` | yes | Integer gameplay updates per second. |
| `clips` | array of [ClipSource](#type-clipsource) (exactly 2) | yes | Exactly boss-telegraph then floor-transition. |

Examples: [input-arena-timeline-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="game-arena-run"></a>

### `/game/arena/run`

Run started.

Emitted once per accepted start/retry before that start's phase event and receipt. Captures the full adopted content, script and timeline. Use run to reset presentation identity; do not use this as a per-tick state update.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Run](#type-run).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `content` | [ContentVersion](#type-contentversion) | yes | Detached game-content version adopted for this run. |
| `script` | [ScriptVersion](#type-scriptversion) | yes | Detached boss script adopted for this run. |
| `timeline` | [TimelineVersion](#type-timelineversion) | yes | Detached presentation sources adopted for this run. |

Examples: [game-arena-run-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="game-arena-attack"></a>

### `/game/arena/attack`

Attack executed.

Emitted only when an attack actually executes, not on every held button frame. Player weapon kind is an ItemKind number; enemy attack kind is an EnemyKind number; grenade and boss_burst are strings. itemId, direction and target are variant-specific. A boss burst emits one attack followed by eight projectile spawns. attackId is not a universal actor ID or a one-to-one identifier for every burst projectile. Use origin for one-shot effects and correlate with the actor/state where needed.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Attack](#type-attack).

**Player weapon**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `0` | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `kind` | `0`, `1`, `2` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `direction` | [Vec2](#type-vec2) | yes | Ground-plane direction; not a world-space target position. |

**Enemy attack**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `integer` (1…2147483647) | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `kind` | `0`, `1`, `2`, `3` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `direction` | [Vec2](#type-vec2) | yes | Ground-plane direction; not a world-space target position. |

**Grenade throw**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `0` | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `kind` | `"grenade"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `target` | [Vec2](#type-vec2) | yes | Bounded world-space grenade landing point. |

**Boss burst**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `integer` (1…2147483647) | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `kind` | `"boss_burst"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |

Examples: [game-arena-attack-grenade-throw](../contracts/arena-v1/examples/messages.json), [game-arena-attack-player-weapon](../contracts/arena-v1/examples/messages.json), [game-arena-attack-enemy-attack](../contracts/arena-v1/examples/messages.json), [game-arena-attack-boss-burst](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "actorId": 0,
  "attackId": 1,
  "itemId": 9,
  "kind": "grenade",
  "order": 9,
  "origin": {
    "x": -2.4619977474212646,
    "y": -1.2553508281707764
  },
  "target": {
    "x": 0.0,
    "y": 5.0
  },
  "tick": 75
}
```

<a id="game-arena-damage"></a>

### `/game/arena/damage`

Damage applied.

Enemy damage is aggregated per target for the gameplay step, in first-hit order, with all contributing attackIds. Enemy deaths are processed next, then incoming player damage. damage is attempted damage before shield absorption and HP clamping; absorbed is shield charge consumed, not HP loss. No impact position, sourceId or damage-type field exists in v1. Obtain position from the displayed actor before despawn or use the separate hit effect.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Damage](#type-damage).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `targetId` | `i32` | yes | Damaged actor ID; 0 is the player. |
| `targetKind` | `"enemy"`, `"player"` | yes | Whether the target is the player or an enemy. |
| `damage` | `i32` | yes | Attempted damage before shield absorption and HP clamping. |
| `attackIds` | array of `i32` | yes | Contributing attack IDs in first-hit accumulation order. |
| `health` | `i32` | yes | HP after applying this operation. |
| `absorbed` | `i32` | yes | Integral shield charge absorbed by this player damage application; zero for enemies. |

Examples: [game-arena-damage-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "absorbed": 0,
  "attackIds": [
    5,
    4
  ],
  "damage": 33,
  "health": 7,
  "order": 4,
  "targetId": 3,
  "targetKind": "enemy",
  "tick": 256
}
```

<a id="game-arena-death"></a>

### `/game/arena/death`

Entity died.

Enemy deaths are emitted in reverse enemy-list order and immediately followed by enemy despawn. Player death uses entityId 0 and string kind player; enemy kind is numeric. Player death precedes Results and the result event, and prevents floor-clear rewards. No position is included; preserve the last displayed transform for the death animation.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Death](#type-death).

**Player**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `entityId` | `0` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `kind` | `"player"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |

**Enemy**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `entityId` | `integer` (1…2147483647) | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `kind` | `0`, `1`, `2`, `3` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |

Examples: [game-arena-death-enemy](../contracts/arena-v1/examples/messages.json), [game-arena-death-player](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "entityId": 3,
  "kind": 0,
  "order": 3,
  "tick": 271
}
```

<a id="game-arena-inventory"></a>

### `/game/arena/inventory`

Inventory changed.

Transfer/upgrade events carry tick, input sequence, source and messageId, but no order field. Consumable events carry tick/order and no single input identity because use intents coalesce. index/slot can be unused zero placeholders for some transfer operations. inventory is the complete post-operation state. Rejected and duplicate commands never repeat the mutation notification.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [InventoryEvent](#type-inventoryevent).

**Transfer or upgrade**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick of this message; snapshots use -1 before the first completed tick. |
| `sequence` | `u64` | yes | Runtime-assigned input queue sequence, not output delivery sequence. |
| `source` | `string` | yes | Producer identity bound to the input. |
| `messageId` | `u64` | yes | Original producer message ID. |
| `operation` | `"/input/arena/take"`, `"/input/arena/equip"`, `"/input/arena/unequip"`, `"/input/arena/discard"`, `"/input/arena/upgrade"` | yes | The input OSC address responsible for this inventory mutation. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `index` | `i32` | yes | Backpack index; an unused zero placeholder for unequip. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

**Consumed item**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `operation` | `"/input/arena/use"` | yes | The input OSC address responsible for this inventory mutation. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

Examples: [game-arena-inventory-transfer-or-upgrade](../contracts/arena-v1/examples/messages.json), [game-arena-inventory-consumed-item](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="game-arena-phase"></a>

### `/game/arena/phase`

Game phase changed.

Emitted for lifecycle phase changes and progression: Opening=0, Preparing=1, Transition=2, Combat=3, Cleared=4, Results=5. Pause/inventory/chest are overlays and do not emit this event. Floor enemies spawn before Combat. Last-enemy clear emits Cleared before transient cleanup and any boss reward; portal entry emits Transition.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Phase](#type-phase).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `previous` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Previous game phase (0..5). |
| `phase` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Current game phase; see the six numeric phase values in the semantic notes. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |
| `floorsCleared` | `i32` | yes | Completed floors in this run. |
| `enemiesDefeated` | `i32` | yes | Total enemy kills in this run, including bosses. |
| `bossesDefeated` | `i32` | yes | Boss kills in this run. |

Examples: [game-arena-phase-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "bossesDefeated": 0,
  "enemiesDefeated": 0,
  "floor": 0,
  "floorsCleared": 0,
  "order": 8,
  "phase": 1,
  "previous": 0,
  "tick": 0
}
```

<a id="game-arena-reward"></a>

### `/game/arena/reward`

Boss-floor reward granted.

Emitted once after a living player clears a floor divisible by five. Contains full healing and generated chest item IDs plus complete inventory. Ordinary floor clears emit phase but no reward event.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Reward](#type-reward).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |
| `health` | `i32` | yes | HP after applying this operation. |
| `itemIds` | array of `i32` | yes | Ordered newly generated chest item IDs. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

Examples: [game-arena-reward-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="game-arena-result"></a>

### `/game/arena/result`

Run result finalized.

Emitted after player death, the Results phase change and transient cleanup. The nested result is captured at death and remains immutable for that completed run. Use it for result animation; use the state snapshot to restore the screen after reconnect/seek.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Result](#type-result).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `result` | [RunResult](#type-runresult) | yes | Immutable values captured at player death. |

Examples: [game-arena-result-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "order": 11,
  "result": {
    "attackMultiplier": 1.149999976158142,
    "bossesDefeated": 2,
    "elapsed": 88.02098846435547,
    "enemiesDefeated": 58,
    "equipmentNames": [
      "Power Shooter",
      "Quick Shooter",
      "Shield",
      "Medkit"
    ],
    "floor": 11,
    "floorsCleared": 10,
    "maxHealth": 130,
    "present": true
  },
  "tick": 5526
}
```

<a id="game-arena-script-fault"></a>

### `/game/arena/script-fault`

Boss script failed.

A late script failure consumes one management tick, emits this fault and the script snapshot, and pauses without partially applying gameplay. No order or run field is present in this payload. Resume cannot bypass it; a new run clears the fault. Treat diagnostic text as display text, not a stable branching key.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ScriptFault](#type-scriptfault).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick consumed when the failure was observed. |
| `enemyId` | `i32` | yes | Boss entity whose request failed before gameplay mutation. |
| `scriptHash` | `string` | yes | Active detached script identity. |
| `diagnostic` | [Diagnostic](#type-diagnostic) | yes | Bounded compile/evaluation/application-contract diagnostic. |

Examples: [game-arena-script-fault-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "tick": 4679,
  "enemyId": 736,
  "scriptHash": "1c25f847ac9a303b6d4e05400556b49be87314a6db2dee62d7211d5228f293c7",
  "diagnostic": {
    "kind": "runtime",
    "message": "Runtime error: contract fault (line 3, position 41)",
    "line": 3,
    "column": 41
  }
}
```

<a id="render-arena-spawn"></a>

### `/render/arena/spawn`

Spawn an enemy, projectile, grenade or effect.

Contains the new entityId, string kind and the complete initial actor state. Actor-state keys are PascalCase, unlike most Arena payloads. Effect kinds are Slash=0, Explosion=1, Hit=2. Spawned objects may also disappear within the same tick; do not rely solely on final state differences for one-shot visuals.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Spawn](#type-spawn).

**enemy**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"enemy"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Enemy](#type-enemy) | yes | Complete actor state at creation. |

**projectile**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"projectile"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Projectile](#type-projectile) | yes | Complete actor state at creation. |

**grenade**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"grenade"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Grenade](#type-grenade) | yes | Complete actor state at creation. |

**effect**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"effect"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Effect](#type-effect) | yes | Complete actor state at creation. |

Examples: [render-arena-spawn-grenade](../contracts/arena-v1/examples/messages.json), [render-arena-spawn-effect](../contracts/arena-v1/examples/messages.json), [render-arena-spawn-enemy](../contracts/arena-v1/examples/messages.json), [render-arena-spawn-projectile](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "entityId": 1,
  "kind": "grenade",
  "order": 10,
  "state": {
    "Damage": 100,
    "Id": 1,
    "Position": {
      "x": -2.4619977474212646,
      "y": -1.2553508281707764
    },
    "Remaining": 0.5,
    "Start": {
      "x": -2.4619977474212646,
      "y": -1.2553508281707764
    },
    "Target": {
      "x": 0.0,
      "y": 5.0
    }
  },
  "tick": 75
}
```

<a id="render-arena-despawn"></a>

### `/render/arena/despawn`

Remove an actor or effect.

Emitted on enemy death, projectile expiry/impact, grenade detonation, effect timeout and transient cleanup. No reason or position is included. Despawn does not necessarily mean death or impact. Lifecycle resets can instead replace the whole state; reconcile against snapshots.

Implementation: [app/src/arena/combat.rs](../../app/src/arena/combat.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [Despawn](#type-despawn).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"enemy"`, `"projectile"`, `"grenade"`, `"effect"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |

Examples: [render-arena-despawn-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "entityId": 1,
  "kind": "grenade",
  "order": 1,
  "tick": 104
}
```

<a id="ui-arena-command"></a>

### `/ui/arena/command`

Discrete command receipt.

Reports acceptance, duplication and reason code. id is the producer message ID; sequence is Runtime input sequence. tick is the current response tick; appliedTick preserves the original application tick for duplicates, or -1 on ID conflict. A successful use receipt does not guarantee consumption. Unknown/malformed commands fail admission rather than emitting an unknown_command receipt. Do not trigger gameplay effects again for duplicates.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [CommandOutcome](#type-commandoutcome).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `sequence` | `u64` | yes | Runtime-assigned input queue sequence, not output delivery sequence. |
| `source` | `string` | yes | Producer identity bound to the input. |
| `id` | `u64` | yes | Producer message ID for a receipt; see type-specific descriptions elsewhere. |
| `tick` | `i64` | yes | Management tick of this message; snapshots use -1 before the first completed tick. |
| `appliedTick` | `i64` | yes | Original application tick; -1 for ID conflicts. |
| `accepted` | `boolean` | yes | Whether the Runtime game operation was accepted. |
| `duplicate` | `boolean` | yes | Whether this response represents a duplicate or reused producer ID. |
| `code` | `"ok"`, `"invalid_state"`, `"out_of_range"`, `"stale_item"`, `"invalid_target"`, `"rule_rejected"`, `"id_conflict"` | yes | Stable result code, not localized display text. |

Examples: [ui-arena-command-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "sequence": 0,
  "source": "host:arena-content",
  "id": 1,
  "tick": 0,
  "appliedTick": 0,
  "accepted": true,
  "duplicate": false,
  "code": "ok"
}
```

<a id="ui-arena-use"></a>

### `/ui/arena/use`

Consumable attempt result.

Emitted once per coalesced attempt on a gameplay step. consumed=true with code ok follows the inventory consumption event. Empty slots, automatic shields, full HP and invalid grenade aim do not consume an item. Successful grenade use then emits attack/spawn; medkit use has no dedicated heal event.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [UseOutcome](#type-useoutcome).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `consumed` | `boolean` | yes | Whether the item was actually consumed by this gameplay attempt. |
| `code` | `"ok"`, `"empty_slot"`, `"automatic_shield"`, `"full_health"`, `"invalid_aim"` | yes | Stable result code, not localized display text. |

Examples: [ui-arena-use-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "code": "empty_slot",
  "consumed": false,
  "itemId": 0,
  "order": 1,
  "slot": 2,
  "tick": 7
}
```

<a id="ui-arena-timeline-event"></a>

### `/ui/arena/timeline/event`

Presentation cue audit.

kind is start, event or stop. Applied events preserve trackIndex/eventIndex and an exact typed OSC bundle (including empty bundles). These audit records follow original game events and precede the final state/presentation pair. Their message order fields are indices in the complete output bundle, not a separate timeline counter. Nested messages are authored cue assignments, not separately broadcast top-level events.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [TimelineEvent](#type-timelineevent).

**Boss start**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"start"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |

**Floor start**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"start"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `fromFloor` | `i32` | yes | Floor being left. |
| `toFloor` | `i32` | yes | Floor being entered. |

**Applied bundle**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"`, `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"event"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `trackIndex` | `u32` | yes | Zero-based authored track index. |
| `eventIndex` | `u32` | yes | Zero-based event index within its authored track. |
| `bundle` | [WireBundle](#type-wirebundle) | yes | Original typed OSC bundle, preserving empty bundles and message/argument order. |

**Stop**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"`, `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"stop"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `reason` | `"new-run"`, `"menu"`, `"lifecycle"`, `"boss-phase-ended"`, `"completed"`, `"replaced"` | yes | Reason the cue instance stopped. |

Examples: [ui-arena-timeline-event-floor-start](../contracts/arena-v1/examples/messages.json), [ui-arena-timeline-event-applied-bundle](../contracts/arena-v1/examples/messages.json), [ui-arena-timeline-event-stop](../contracts/arena-v1/examples/messages.json), [ui-arena-timeline-event-boss-start](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "clipId": "floor-transition",
  "cueId": "r1:c1",
  "fromFloor": 0,
  "kind": "start",
  "offsetTick": 0,
  "order": 1,
  "run": 1,
  "tick": 185,
  "toFloor": 1
}
```

<a id="ui-arena-state"></a>

### `/ui/arena/state`

Complete gameplay state.

Emitted at the end of every management tick and on inspection, even when paused. Contains current actor transforms, inventory, overlays and result. There is no separate Arena transform event. Reconcile the whole state on lifecycle changes and snapshots; publish together with presentation only when tick and simulation-step counts match.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ArenaState](#type-arenastate).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Last completed source tick; -1 before the first update. |
| `simulationSteps` | `u64` | yes | Number of gameplay steps, excluding paused/opening/results ticks. |
| `phase` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Reference ArenaPhase: opening=0, preparation=1, transition=2, combat=3, cleared=4, results=5. |
| `overlay` | `"none"`, `"pause"`, `"inventory"`, `"chest"` | yes | Runtime-owned pause/interaction overlay. |
| `floor` | `i32` | yes | Current floor; preparation is zero. |
| `elapsed` | `finite f32` | yes | Gameplay elapsed seconds, accumulated using reference f32 arithmetic. |
| `playerPosition` | [Vec2](#type-vec2) | yes | Authoritative player ground-plane position. |
| `aimDirection` | [Vec2](#type-vec2) | yes | Last valid normalized aim direction. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete item ownership and health/shield clock projection. |
| `chestAvailable` | `boolean` | yes | Whether the current safe phase offers a chest. |
| `portalAvailable` | `boolean` | yes | Whether the current phase offers a portal (progression migrates in stage 5). |
| `enemiesDefeated` | `i32` | yes | Total enemies defeated in this run. |
| `bossesDefeated` | `i32` | yes | Total bosses defeated in this run. |
| `floorsCleared` | `i32` | yes | Cleared floors in this run. |
| `nextEntityId` | `i32` | yes | Next run-local entity/effect ID. |
| `transitionRemaining` | `finite f32` | yes | Remaining transition seconds; transitions do not advance the elapsed run time. |
| `portalArmed` | `boolean` | yes | Portal must be exited before it can trigger another transition. |
| `weaponCooldowns` | array of `finite f32` (exactly 2) | yes | Weapon A/B cooldown seconds. |
| `enemies` | array of [Enemy](#type-enemy) | yes | Enemies in stable spawn order. |
| `projectiles` | array of [Projectile](#type-projectile) | yes | Active projectiles in allocation order. |
| `grenades` | array of [Grenade](#type-grenade) | yes | Active grenades in allocation order. |
| `effects` | array of [Effect](#type-effect) | yes | Active presentation effects in allocation order. |
| `result` | [RunResult](#type-runresult) | yes | Detached immutable result values when the player dies. |

Examples: [ui-arena-state-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="render-arena-presentation"></a>

### `/render/arena/presentation`

Complete timeline presentation state.

Emitted after state at each tick and on inspection. Includes live boss cues and the optional floor fade. Render radius/intensity/opacity directly; Unity frames must not advance cue offsets. Pause, overlays and faults freeze simulation steps while management ticks continue. Seek may move time backwards.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [PresentationSnapshot](#type-presentationsnapshot).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `contractVersion` | `1` | yes | Arena presentation schema. |
| `run` | `u64` | yes | Number of accepted starts. |
| `tick` | `i64` | yes | Current management tick, including paused ticks. |
| `simulationStep` | `u64` | yes | Authoritative cumulative successful gameplay step count. |
| `bosses` | array of [BossCue](#type-bosscue) | yes | Live warnings sorted by entity identifier. |
| `floor` | [FloorCue](#type-floorcue) or `null` | yes | At most one live floor fade. |

Examples: [render-arena-presentation-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "contractVersion": 1,
  "run": 0,
  "tick": -1,
  "simulationStep": 0,
  "bosses": [],
  "floor": null
}
```

<a id="ui-arena-content"></a>

### `/ui/arena/content`

Active and pending game content.

Emitted on inspection and successful start/content stage, not every tick. active is null before a run and retained after returning to the menu. Pending content is adopted only on start/retry.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ContentSnapshot](#type-contentsnapshot).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Session-local run number, incremented by every successful start/retry. |
| `active` | [ContentVersion](#type-contentversion) or `null` | yes | Configuration fixed for the current or most recently completed run. |
| `pending` | [ContentVersion](#type-contentversion) | yes | Last valid candidate to use at the next start. |

Examples: [ui-arena-content-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="ui-arena-script"></a>

### `/ui/arena/script`

Active and pending boss script.

Emitted on inspection, start/script stage and late faults. Includes active/pending detached source and nullable fault. Staging a repaired script does not repair the current run; start a new run.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [ScriptSnapshot](#type-scriptsnapshot).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Number of started runs. |
| `active` | [ScriptVersion](#type-scriptversion) or `null` | yes | Rules selected when the current or most recent run began. |
| `pending` | [ScriptVersion](#type-scriptversion) | yes | Validated candidate to adopt on start/retry. |
| `fault` | [ScriptFault](#type-scriptfault) or `null` | yes | Late evaluation failure; cleared only by starting a new run. |

Examples: [ui-arena-script-example](../contracts/arena-v1/examples/messages.json).

Decoded JSON payload example (inside OSC `args[0].value`):

```json
{
  "run": 0,
  "active": null,
  "pending": {
    "hash": "1972fdeaaed2d2e6ff349409087a20440683b1aa90f0199c2f7e0c7a22564025",
    "sourceSha256": "cc75bd728a7fcddaf067e13bf330e650b57c26530bc805ed4683e5f8bb711af1",
    "source": "// Arena boss contract 1. Context is a copied JSON value; actions have no side effects.\n// Rust advances the f32 phase timer and applies radial shots in the reference order.\nfn boss(input) {\n    if input.phase == 0 {\n        if input.timerExpired {\n            return #{action: \"telegraph\", duration: 0.8};\n        }\n        return #{action: \"pursue\", duration: 0.0};\n    }\n    if input.phase == 1 {\n        if input.timerExpired {\n            return #{action: \"burst\", duration: 1.0};\n        }\n        return #{action: \"wait\", duration: 0.0};\n    }\n    if input.timerExpired {\n        return #{action: \"recover\", duration: 3.0};\n    }\n    #{action: \"wait\", duration: 0.0}\n}\n",
    "contractVersion": 1,
    "policyVersion": "kitu-rhai-json-v1",
    "rhaiVersion": "1.26.0"
  },
  "fault": null
}
```

<a id="ui-arena-timeline"></a>

### `/ui/arena/timeline`

Active and pending timeline sources.

Emitted on inspection and successful start/timeline stage. Same-tick updates are coalesced into a complete snapshot after presentation has advanced. Includes detached TSQ1 bytes and current presentation; not a command to independently play those bytes in Unity.

Implementation: [app/src/arena.rs](../../app/src/arena.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `payload` | `str` | JSON document matching the payload definition below. |

Payload: [TimelineSnapshot](#type-timelinesnapshot).

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Number of accepted starts. |
| `active` | [TimelineVersion](#type-timelineversion) or `null` | yes | Sources selected at the last accepted start. |
| `pending` | [TimelineVersion](#type-timelineversion) | yes | Validated sources to adopt on the next start/retry. |
| `presentation` | [PresentationSnapshot](#type-presentationsnapshot) | yes | Current cue clocks and values. |

Examples: [ui-arena-timeline-example](../contracts/arena-v1/examples/messages.json).

The full typed OSC example is in the linked corpus; large state/source payloads are not truncated into misleading JSON here.

<a id="render-arena-cue-boss"></a>

### `/render/arena/cue/boss`

Assign boss warning radius and intensity.

Allowed only inside boss-telegraph clips. Radius is 0.25..8 world units; intensity is 0..1. Every clip initializes values at offset zero. An actual boss phase 0→1 creates the cue; its last assignment persists until the boss leaves telegraph or dies. Runtime publishes the resulting presentation snapshot.

Implementation: [app/src/arena/presentation.rs](../../app/src/arena/presentation.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `radius` | `float` | World radius, inclusive range 0.25..8. |
| 1 | `intensity` | `float` | Inclusive range 0..1. |

Examples: [render-arena-cue-boss-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/render/arena/cue/boss",
  "args": [
    {
      "type": "float",
      "value": 3.0
    },
    {
      "type": "float",
      "value": 0.44999998807907104
    }
  ]
}
```

<a id="render-arena-cue-floor"></a>

### `/render/arena/cue/floor`

Assign floor fade opacity.

Allowed only inside floor-transition clips. Opacity is 0..1; initialize at offset zero and end with opacity zero. Entering Transition starts the cue; it may outlive the transition into the next floor. Its last event removes it. Unity draws the fade behind the HUD.

Implementation: [app/src/arena/presentation.rs](../../app/src/arena/presentation.rs).

| Argument index | Name | OSC tag | Meaning |
| --- | --- | --- | --- |
| 0 | `opacity` | `float` | Inclusive range 0..1. |

Examples: [render-arena-cue-floor-example](../contracts/arena-v1/examples/messages.json).

```json
{
  "address": "/render/arena/cue/floor",
  "args": [
    {
      "type": "float",
      "value": 0.0
    }
  ]
}
```

## Payload and shared type reference

All object fields are required unless explicitly marked optional. Objects reject unregistered fields in the producer contract. Every nested type is linked below.

<a id="type-enemy"></a>

### Enemy

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `Id` | `i32` | yes | Run-local entity ID. |
| `Kind` | `0`, `1`, `2`, `3` | yes | Pursuer=0, shooter=1, heavy=2, boss=3. |
| `Position` | [Vec2](#type-vec2) | yes | Ground-plane position. |
| `Health` | `i32` | yes | Current HP. |
| `MaxHealth` | `i32` | yes | Initial scaled HP. |
| `Radius` | `finite f32` | yes | Collision radius. |
| `Speed` | `finite f32` | yes | Movement units per second. |
| `Damage` | `i32` | yes | Scaled attack damage. |
| `AttackInterval` | `finite f32` | yes | Attack interval in seconds. |
| `AttackRange` | `finite f32` | yes | Movement stops at this attack distance. |
| `AttackCooldown` | `finite f32` | yes | Remaining seconds before the next attack. |
| `BossState` | `i32` | yes | Pursuit=0, telegraph=1, recovery=2. |
| `PhaseRemaining` | `finite f32` | yes | Remaining boss behavior phase seconds. |

<a id="type-projectile"></a>

### Projectile

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `Id` | `i32` | yes | Run-local entity ID. |
| `Position` | [Vec2](#type-vec2) | yes | Current position. |
| `Direction` | [Vec2](#type-vec2) | yes | Travel direction. |
| `Speed` | `finite f32` | yes | Movement units per second. |
| `DistanceRemaining` | `finite f32` | yes | Remaining travel range. |
| `Damage` | `i32` | yes | Damage fixed at firing. |
| `EnemyOwned` | `boolean` | yes | Whether the projectile targets the player. |
| `Radius` | `finite f32` | yes | Swept collision radius. |

<a id="type-grenade"></a>

### Grenade

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `Id` | `i32` | yes | Run-local entity ID. |
| `Start` | [Vec2](#type-vec2) | yes | Throw origin. |
| `Target` | [Vec2](#type-vec2) | yes | Bounded landing point. |
| `Position` | [Vec2](#type-vec2) | yes | Current interpolated position. |
| `Remaining` | `finite f32` | yes | Remaining flight seconds. |
| `Damage` | `i32` | yes | Scaled damage fixed at throw. |

<a id="type-effect"></a>

### Effect

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `Id` | `i32` | yes | Run-local effect ID. |
| `Kind` | `0`, `1`, `2` | yes | Slash=0, explosion=1, hit=2. |
| `Position` | [Vec2](#type-vec2) | yes | Ground-plane origin. |
| `Direction` | [Vec2](#type-vec2) | yes | Presentation direction. |
| `Radius` | `finite f32` | yes | Visible radius. |
| `Remaining` | `finite f32` | yes | Remaining lifetime seconds. |

<a id="type-runresult"></a>

### RunResult

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `present` | `boolean` | yes | Whether a death result exists. |
| `floor` | `i32` | yes | Floor reached. |
| `enemiesDefeated` | `i32` | yes | Enemy kills. |
| `bossesDefeated` | `i32` | yes | Boss kills. |
| `floorsCleared` | `i32` | yes | Cleared floors. |
| `maxHealth` | `i32` | yes | HP capacity at death. |
| `elapsed` | `finite f32` | yes | Run elapsed time. |
| `attackMultiplier` | `finite f32` | yes | Damage multiplier at death. |
| `equipmentNames` | array of `string` | yes | Copied names in equipment slot order, or an empty list before death. |

<a id="type-arenastate"></a>

### ArenaState

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Last completed source tick; -1 before the first update. |
| `simulationSteps` | `u64` | yes | Number of gameplay steps, excluding paused/opening/results ticks. |
| `phase` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Reference ArenaPhase: opening=0, preparation=1, transition=2, combat=3, cleared=4, results=5. |
| `overlay` | `"none"`, `"pause"`, `"inventory"`, `"chest"` | yes | Runtime-owned pause/interaction overlay. |
| `floor` | `i32` | yes | Current floor; preparation is zero. |
| `elapsed` | `finite f32` | yes | Gameplay elapsed seconds, accumulated using reference f32 arithmetic. |
| `playerPosition` | [Vec2](#type-vec2) | yes | Authoritative player ground-plane position. |
| `aimDirection` | [Vec2](#type-vec2) | yes | Last valid normalized aim direction. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete item ownership and health/shield clock projection. |
| `chestAvailable` | `boolean` | yes | Whether the current safe phase offers a chest. |
| `portalAvailable` | `boolean` | yes | Whether the current phase offers a portal (progression migrates in stage 5). |
| `enemiesDefeated` | `i32` | yes | Total enemies defeated in this run. |
| `bossesDefeated` | `i32` | yes | Total bosses defeated in this run. |
| `floorsCleared` | `i32` | yes | Cleared floors in this run. |
| `nextEntityId` | `i32` | yes | Next run-local entity/effect ID. |
| `transitionRemaining` | `finite f32` | yes | Remaining transition seconds; transitions do not advance the elapsed run time. |
| `portalArmed` | `boolean` | yes | Portal must be exited before it can trigger another transition. |
| `weaponCooldowns` | array of `finite f32` (exactly 2) | yes | Weapon A/B cooldown seconds. |
| `enemies` | array of [Enemy](#type-enemy) | yes | Enemies in stable spawn order. |
| `projectiles` | array of [Projectile](#type-projectile) | yes | Active projectiles in allocation order. |
| `grenades` | array of [Grenade](#type-grenade) | yes | Active grenades in allocation order. |
| `effects` | array of [Effect](#type-effect) | yes | Active presentation effects in allocation order. |
| `result` | [RunResult](#type-runresult) | yes | Detached immutable result values when the player dies. |

<a id="type-item"></a>

### Item

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `id` | `i32` | yes | Run-local instance identity. |
| `kind` | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` | yes | C# ItemKind discriminant: blade, shooter, heavy, medkit, grenade, shield, HP upgrade, attack upgrade. |
| `damage` | `i32` | yes | Unscaled base damage. |
| `shield` | `i32` | yes | Remaining integral shield charge. |
| `name` | `string` | yes | Display name. |
| `interval` | `finite f32` | yes | Weapon interval in seconds. |
| `shieldFraction` | `finite f32` | yes | Fractional shield recovery retained across transfers. |

<a id="type-inventory"></a>

### Inventory

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `health` | `i32` | yes | Current HP; zero prevents all further consumption, transfer or healing. |
| `maxHealth` | `i32` | yes | Current HP and shield capacity. |
| `nextItemId` | `i32` | yes | Last allocated item ID (matching the reference field name). |
| `attackUpgrades` | `i32` | yes | Number of consumed attack upgrades. |
| `attackMultiplier` | `finite f32` | yes | Derived attack multiplier. |
| `shieldDelayRemaining` | `finite f32` | yes | Shared delay before equipped shields may recover. |
| `damagedThisUpdate` | `boolean` | yes | Prevents recovery throughout an update that received damage. |
| `backpack` | array of [Item](#type-item) (exactly 3) | yes | Three stable backpack positions. |
| `equipment` | array of [Item](#type-item) (exactly 4) | yes | Weapon A/B and item A/B, in that order. |
| `chest` | array of [Item](#type-item) | yes | Ordered available chest items. |

<a id="type-contentversion"></a>

### ContentVersion

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of the canonical evaluated values. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of legacy TMD bytes, or the complete ordered source provenance. |
| `tanuRevision` | `string` or `null` | no | Tanu API revision that evaluated the source. |
| `provenance` | [ContentProvenance](#type-contentprovenance) or `null` | no | Detached source kinds, digests and field origins; never filesystem paths. |
| `values` | [ArenaConfig](#type-arenaconfig) | yes | Complete values needed to reproduce gameplay without re-evaluating a file. |

<a id="type-contentsnapshot"></a>

### ContentSnapshot

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Session-local run number, incremented by every successful start/retry. |
| `active` | [ContentVersion](#type-contentversion) or `null` | yes | Configuration fixed for the current or most recently completed run. |
| `pending` | [ContentVersion](#type-contentversion) | yes | Last valid candidate to use at the next start. |

<a id="type-itemrule"></a>

### ItemRule

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `id` | `string` | yes | Stable key referenced by chest entries; `starter` names the initial weapon. |
| `name` | `string` | yes | Unique displayed name. |
| `kind` | `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7` | yes | Reference ItemKind discriminant, 0 through 7. |
| `damage` | `i32` | yes | Preparation damage (grenade damage is also fixed at item creation). |
| `bossDamage` | `i32` | yes | Repeating boss chest damage. |
| `interval` | `finite f32` | yes | Weapon cooldown in seconds; zero for non-weapons. |

<a id="type-enemyrule"></a>

### EnemyRule

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `kind` | `0`, `1`, `2`, `3` | yes | Pursuer=0, shooter=1, heavy=2, boss=3. |
| `health` | `i32` | yes | Base HP. |
| `damage` | `i32` | yes | Base attack damage. |
| `speed` | `finite f32` | yes | Ground units per second. |
| `range` | `finite f32` | yes | Attack distance in ground units. |
| `interval` | `finite f32` | yes | Attack interval in seconds. |
| `radius` | `finite f32` | yes | Collision radius in ground units. |

<a id="type-difficulty"></a>

### Difficulty

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `healthGrowth` | `finite f32` | yes | HP multiplier increase per floor after floor one. |
| `damageGrowth` | `finite f32` | yes | Attack multiplier increase per floor after floor one. |

<a id="type-chestentry"></a>

### ChestEntry

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `phase` | [ChestPhase](#type-chestphase) | yes | Generation point. |
| `itemId` | `string` | yes | Referenced item archetype key. |

<a id="type-arenaconfig"></a>

### ArenaConfig

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `schemaVersion` | `1` | yes | Typed content schema, independent of transport schema. |
| `items` | array of [ItemRule](#type-itemrule) | yes | Item definitions, including `starter`. |
| `enemies` | array of [EnemyRule](#type-enemyrule) | yes | Exactly one definition for each enemy kind. |
| `difficulty` | [Difficulty](#type-difficulty) | yes | Floor scaling. |
| `chests` | array of [ChestEntry](#type-chestentry) | yes | Ordered chest contents. |

<a id="type-sourcedescriptor"></a>

### SourceDescriptor

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `layer` | [Layer](#type-layer) | yes | Position in the fixed override order. |
| `format` | [SourceFormat](#type-sourceformat) | yes | Actual storage format. |
| `schemaVersion` | `u32` | yes | Arena source schema. |
| `evaluator` | `string` | yes | Tanu revision or the SQLite scalar-reading policy. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | Raw TMD digest or normalized queried SQLite snapshot digest. |

<a id="type-contentprovenance"></a>

### ContentProvenance

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `version` | `u32` | yes | Provenance encoding version. |
| `sources` | array of [SourceDescriptor](#type-sourcedescriptor) | yes | Declared sources in base, difficulty, event, debug order. |
| `origins` | map from string to [Layer](#type-layer) | yes | RFC6901-escaped semantic field paths and their winning layers. |

<a id="type-scriptversion"></a>

### ScriptVersion

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of source plus the exact contract and execution policy identities. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of the UTF-8 source bytes. |
| `source` | `string` | yes | Detached source; never a filename or a reference to authoring state. |
| `contractVersion` | `1` | yes | Arena boss context/action schema. |
| `policyVersion` | `string` | yes | Generic sandbox policy identity. |
| `rhaiVersion` | `string` | yes | Exact Rhai dependency version. |

<a id="type-scriptfault"></a>

### ScriptFault

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick consumed when the failure was observed. |
| `enemyId` | `i32` | yes | Boss entity whose request failed before gameplay mutation. |
| `scriptHash` | `string` | yes | Active detached script identity. |
| `diagnostic` | [Diagnostic](#type-diagnostic) | yes | Bounded compile/evaluation/application-contract diagnostic. |

<a id="type-scriptsnapshot"></a>

### ScriptSnapshot

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Number of started runs. |
| `active` | [ScriptVersion](#type-scriptversion) or `null` | yes | Rules selected when the current or most recent run began. |
| `pending` | [ScriptVersion](#type-scriptversion) | yes | Validated candidate to adopt on start/retry. |
| `fault` | [ScriptFault](#type-scriptfault) or `null` | yes | Late evaluation failure; cleared only by starting a new run. |

<a id="type-clipsource"></a>

### ClipSource

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `id` | `string` | yes | Stable application clip identifier. |
| `sourceSha256` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of the exact bytes, including supported TSQ1 framing. |
| `bytes` | array of `integer` (0…255) (at most 8192) | yes | Exact detached TSQ1 file bytes, at most 8 KiB. Binary validity is checked by the TSQ1 decoder. |

<a id="type-timelineversion"></a>

### TimelineVersion

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `hash` | `string`; pattern `^[0-9a-fA-F]{64}$` | yes | SHA-256 of contract, tick rate and ordered clip identities. |
| `contractVersion` | `1` | yes | Arena presentation schema. |
| `tickRate` | `60` | yes | Integer gameplay updates per second. |
| `clips` | array of [ClipSource](#type-clipsource) (exactly 2) | yes | Exactly boss-telegraph then floor-transition. |

<a id="type-bosscue"></a>

### BossCue

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `id` | `string` | yes | Unique instance identity within the run. |
| `clipId` | `"boss-telegraph"` | yes | Source clip identifier. |
| `entityId` | `i32` | yes | Authoritative enemy entity identifier. |
| `floor` | `i32` | yes | Floor where this warning started. |
| `startedTick` | `i64` | yes | Management tick of the triggering state change. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since the trigger. |
| `nextEventIndex` | `u32` | yes | Number of consumed TSQ1 bundle events. |
| `eventCount` | `u32` | yes | Total authored bundle events, including empty bundles. |
| `radius` | `number` (0.25…8) | yes | Last authored world-space warning radius. |
| `intensity` | `number` (0…1) | yes | Last authored warning intensity, in [0, 1]. |

<a id="type-floorcue"></a>

### FloorCue

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `id` | `string` | yes | Unique instance identity within the run. |
| `clipId` | `"floor-transition"` | yes | Source clip identifier. |
| `fromFloor` | `i32` | yes | Floor being left. |
| `toFloor` | `i32` | yes | Floor being entered. |
| `startedTick` | `i64` | yes | Management tick of the trigger. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since the trigger. |
| `nextEventIndex` | `u32` | yes | Number of consumed TSQ1 bundle events. |
| `eventCount` | `u32` | yes | Total authored bundle events. |
| `opacity` | `number` (0…1) | yes | Last authored opacity, in [0, 1]. |

<a id="type-presentationsnapshot"></a>

### PresentationSnapshot

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `contractVersion` | `1` | yes | Arena presentation schema. |
| `run` | `u64` | yes | Number of accepted starts. |
| `tick` | `i64` | yes | Current management tick, including paused ticks. |
| `simulationStep` | `u64` | yes | Authoritative cumulative successful gameplay step count. |
| `bosses` | array of [BossCue](#type-bosscue) | yes | Live warnings sorted by entity identifier. |
| `floor` | [FloorCue](#type-floorcue) or `null` | yes | At most one live floor fade. |

<a id="type-timelinesnapshot"></a>

### TimelineSnapshot

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `run` | `u64` | yes | Number of accepted starts. |
| `active` | [TimelineVersion](#type-timelineversion) or `null` | yes | Sources selected at the last accepted start. |
| `pending` | [TimelineVersion](#type-timelineversion) | yes | Validated sources to adopt on the next start/retry. |
| `presentation` | [PresentationSnapshot](#type-presentationsnapshot) | yes | Current cue clocks and values. |

<a id="type-vec2"></a>

### Vec2

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `x` | `finite f32` | yes | World X, in Unity world units. |
| `y` | `finite f32` | yes | World Z, in Unity world units; this is not vertical height. |

<a id="type-layer"></a>

### Layer

`"base"`, `"difficulty"`, `"event"`, `"debug"`

<a id="type-sourceformat"></a>

### SourceFormat

`"tmd"`, `"sqlite"`

<a id="type-chestphase"></a>

### ChestPhase

`"preparing"`, `"boss"`

<a id="type-diagnostic"></a>

### Diagnostic

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `kind` | `string` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `message` | `string` | yes | Bounded diagnostic text; not a stable contract code. |
| `line` | `u64` or `null` | yes | Optional source line reported by the script engine. |
| `column` | `u64` or `null` | yes | Optional source column reported by the script engine. |

<a id="type-attack"></a>

### Attack

**Player weapon**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `0` | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `kind` | `0`, `1`, `2` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `direction` | [Vec2](#type-vec2) | yes | Ground-plane direction; not a world-space target position. |

**Enemy attack**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `integer` (1…2147483647) | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `kind` | `0`, `1`, `2`, `3` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `direction` | [Vec2](#type-vec2) | yes | Ground-plane direction; not a world-space target position. |

**Grenade throw**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `0` | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `kind` | `"grenade"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |
| `target` | [Vec2](#type-vec2) | yes | Bounded world-space grenade landing point. |

**Boss burst**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `actorId` | `integer` (1…2147483647) | yes | Attacking actor ID; 0 is the player. |
| `attackId` | `i32` | yes | Attack correlation ID; see burst limitations in the semantic notes. |
| `kind` | `"boss_burst"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `origin` | [Vec2](#type-vec2) | yes | World-space origin of the attack. |

<a id="type-damage"></a>

### Damage

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `targetId` | `i32` | yes | Damaged actor ID; 0 is the player. |
| `targetKind` | `"enemy"`, `"player"` | yes | Whether the target is the player or an enemy. |
| `damage` | `i32` | yes | Attempted damage before shield absorption and HP clamping. |
| `attackIds` | array of `i32` | yes | Contributing attack IDs in first-hit accumulation order. |
| `health` | `i32` | yes | HP after applying this operation. |
| `absorbed` | `i32` | yes | Integral shield charge absorbed by this player damage application; zero for enemies. |

<a id="type-death"></a>

### Death

**Player**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `entityId` | `0` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `kind` | `"player"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |

**Enemy**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `entityId` | `integer` (1…2147483647) | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `kind` | `0`, `1`, `2`, `3` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |

<a id="type-inventoryevent"></a>

### InventoryEvent

**Transfer or upgrade**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick of this message; snapshots use -1 before the first completed tick. |
| `sequence` | `u64` | yes | Runtime-assigned input queue sequence, not output delivery sequence. |
| `source` | `string` | yes | Producer identity bound to the input. |
| `messageId` | `u64` | yes | Original producer message ID. |
| `operation` | `"/input/arena/take"`, `"/input/arena/equip"`, `"/input/arena/unequip"`, `"/input/arena/discard"`, `"/input/arena/upgrade"` | yes | The input OSC address responsible for this inventory mutation. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `index` | `i32` | yes | Backpack index; an unused zero placeholder for unequip. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

**Consumed item**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `operation` | `"/input/arena/use"` | yes | The input OSC address responsible for this inventory mutation. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

<a id="type-phase"></a>

### Phase

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `previous` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Previous game phase (0..5). |
| `phase` | `0`, `1`, `2`, `3`, `4`, `5` | yes | Current game phase; see the six numeric phase values in the semantic notes. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |
| `floorsCleared` | `i32` | yes | Completed floors in this run. |
| `enemiesDefeated` | `i32` | yes | Total enemy kills in this run, including bosses. |
| `bossesDefeated` | `i32` | yes | Boss kills in this run. |

<a id="type-reward"></a>

### Reward

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |
| `health` | `i32` | yes | HP after applying this operation. |
| `itemIds` | array of `i32` | yes | Ordered newly generated chest item IDs. |
| `inventory` | [Inventory](#type-inventory) | yes | Complete post-operation inventory state. |

<a id="type-result"></a>

### Result

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `result` | [RunResult](#type-runresult) | yes | Immutable values captured at player death. |

<a id="type-run"></a>

### Run

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `content` | [ContentVersion](#type-contentversion) | yes | Detached game-content version adopted for this run. |
| `script` | [ScriptVersion](#type-scriptversion) | yes | Detached boss script adopted for this run. |
| `timeline` | [TimelineVersion](#type-timelineversion) | yes | Detached presentation sources adopted for this run. |

<a id="type-spawn"></a>

### Spawn

**enemy**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"enemy"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Enemy](#type-enemy) | yes | Complete actor state at creation. |

**projectile**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"projectile"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Projectile](#type-projectile) | yes | Complete actor state at creation. |

**grenade**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"grenade"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Grenade](#type-grenade) | yes | Complete actor state at creation. |

**effect**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"effect"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `state` | [Effect](#type-effect) | yes | Complete actor state at creation. |

<a id="type-despawn"></a>

### Despawn

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `kind` | `"enemy"`, `"projectile"`, `"grenade"`, `"effect"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |

<a id="type-commandoutcome"></a>

### CommandOutcome

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `sequence` | `u64` | yes | Runtime-assigned input queue sequence, not output delivery sequence. |
| `source` | `string` | yes | Producer identity bound to the input. |
| `id` | `u64` | yes | Producer message ID for a receipt; see type-specific descriptions elsewhere. |
| `tick` | `i64` | yes | Management tick of this message; snapshots use -1 before the first completed tick. |
| `appliedTick` | `i64` | yes | Original application tick; -1 for ID conflicts. |
| `accepted` | `boolean` | yes | Whether the Runtime game operation was accepted. |
| `duplicate` | `boolean` | yes | Whether this response represents a duplicate or reused producer ID. |
| `code` | `"ok"`, `"invalid_state"`, `"out_of_range"`, `"stale_item"`, `"invalid_target"`, `"rule_rejected"`, `"id_conflict"` | yes | Stable result code, not localized display text. |

<a id="type-useoutcome"></a>

### UseOutcome

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `slot` | `i32` | yes | Equipment slot (WeaponA=0, WeaponB=1, ItemA=2, ItemB=3); unused transfer fields can be zero. |
| `itemId` | `i32` | yes | Run-local item instance ID (a distinct namespace from actor IDs). |
| `consumed` | `boolean` | yes | Whether the item was actually consumed by this gameplay attempt. |
| `code` | `"ok"`, `"empty_slot"`, `"automatic_shield"`, `"full_health"`, `"invalid_aim"` | yes | Stable result code, not localized display text. |

<a id="type-timelineevent"></a>

### TimelineEvent

**Boss start**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"start"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `entityId` | `i32` | yes | Run-local actor/effect identifier; player is 0 where applicable. |
| `floor` | `i32` | yes | Current floor; Preparing is floor zero. |

**Floor start**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"start"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `fromFloor` | `i32` | yes | Floor being left. |
| `toFloor` | `i32` | yes | Floor being entered. |

**Applied bundle**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"`, `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"event"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `trackIndex` | `u32` | yes | Zero-based authored track index. |
| `eventIndex` | `u32` | yes | Zero-based event index within its authored track. |
| `bundle` | [WireBundle](#type-wirebundle) | yes | Original typed OSC bundle, preserving empty bundles and message/argument order. |

**Stop**

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `tick` | `i64` | yes | Management tick at which this event was emitted. |
| `order` | `u64` | yes | Zero-based message index within the emitted OSC bundle, including other message families. |
| `run` | `u64` | yes | Session-local number incremented by each successful start/retry. |
| `cueId` | `string` | yes | Run-local presentation cue identity. |
| `clipId` | `"boss-telegraph"`, `"floor-transition"` | yes | Authored clip identity. |
| `offsetTick` | `u64` | yes | Successful gameplay steps since this cue started. |
| `kind` | `"stop"` | yes | Variant discriminator. Numeric namespaces depend on the message/actor; see semantic notes. |
| `reason` | `"new-run"`, `"menu"`, `"lifecycle"`, `"boss-phase-ended"`, `"completed"`, `"replaced"` | yes | Reason the cue instance stopped. |

<a id="type-wirearg"></a>

### WireArg

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `type` | `"int"` | yes | OSC scalar tag. |
| `value` | `i32` | yes | Value interpreted according to its exact OSC tag. |

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `type` | `"int64"` | yes | OSC scalar tag. |
| `value` | `i64` | yes | Value interpreted according to its exact OSC tag. |

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `type` | `"float"` | yes | OSC scalar tag. |
| `value` | `finite f32` | yes | Finite f32; exact f32 transport encoding is checked by the wire codec. |

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `type` | `"str"` | yes | OSC scalar tag. |
| `value` | `string` | yes | Value interpreted according to its exact OSC tag. |

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `type` | `"bool"` | yes | OSC scalar tag. |
| `value` | `boolean` | yes | Value interpreted according to its exact OSC tag. |

<a id="type-wiremessage"></a>

### WireMessage

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `address` | `string` | yes | Exact OSC address. |
| `args` | array of [WireArg](#type-wirearg) | yes | Ordered typed OSC scalar arguments. |

<a id="type-wirebundle"></a>

### WireBundle

| Field | Type / range | Required | Meaning |
| --- | --- | --- | --- |
| `messages` | array of [WireMessage](#type-wiremessage) | yes | Ordered OSC messages; an empty list remains a valid bundle. |

<!-- END GENERATED ARENA CONTRACT -->

## Reading the contract

- **Input commands** express intent. Runtime owns acceptance and all outcomes.
- **Game events** describe completed actions; use them for one-shot animation,
  audio and notifications. Do not infer all actions from snapshot differences.
- **Object lifecycle** messages describe creation/removal, not independent clocks.
- **State snapshots** replace current state and restore it after reconnect/seek.
- **TSQ1 clip messages** are nested authored assignments, not top-level output.

The scope is all `/input/arena/*`, `/game/arena/*`, `/ui/arena/*` and
`/render/arena/*` messages. HTTP/Admin inspection responses, `/host/arena/*`, the
legacy `/input/move` demo, and generic Kitu runtime messages are separate APIs.
For transport framing, identity, admission and scalar encoding, see
[application wire v1](arena-application-wire.md) and
[native ABI](arena-native-abi.md). These layers are not replaced by this catalog.

## Shared timing, identity and rendering rules

Runtime advances at 60 management ticks/second. Gameplay and TSQ1 cues advance
only on successful gameplay steps; paused/overlay/fault ticks still process
management inputs. `tick` starts at -1 for an initial inspection. Gameplay elapsed
seconds and simulation-step counts are different: transition steps advance the
latter without increasing the former. See [runtime ordering](arena-runtime-contract.md#tick-and-pause-semantics).

Preserve batch, bundle and message order. An event's `order`, when present, is
its zero-based index in the entire emitted bundle, not just the game events.
There is no universal payload envelope: transfers and script faults omit order;
most game events omit run/session. Session comes from the connection; run comes
from `/game/arena/run` or coherent source/presentation snapshots. Actor and item
IDs are run-local, player actor ID is 0; do not confuse actor and item ID spaces.
A boss burst's attack ID is not a complete map to its eight projectiles.

Vectors use `{x,y}` on the ground plane: x is Unity X, y is Unity Z. Distances
are world units; speeds are units/second; durations are seconds unless named
tick/offsetTick. Numeric enum namespaces are separate (item, enemy, effect,
phase). Actor projection fields deliberately use PascalCase; most other objects
use camelCase. Preserve exact spelling and casing.

Each JSON-payload message has one OSC `str` argument. Decode that string as JSON
before applying its payload schema. Raw OSC arguments retain `int` (i32), `int64`
(i64), finite `float` (f32), `str`, or `bool`; integer IDs/ticks must not travel
through a floating-point intermediate. JSON Schema validates mathematical values,
not MessagePack marker widths, hash correctness or TSQ1 bytes; the existing codecs
and application validators remain authoritative for those checks.

Apply an entire output batch on the Unity main thread before publishing state.
Match state.tick/presentation.tick and state.simulationSteps/presentation.simulationStep.
On initial/reconnect/seek snapshots, replace display state without replaying old
sounds or notifications. Seeking can go backwards. There is no Arena transform,
heal, shield-break or pause domain event: use documented snapshots and existing
events as appropriate. Despawn is not proof of a hit or a death. Preserve a dying
actor's last transform if its death animation outlives removal from authoritative
state. Current `KituArenaClient.ApplyBatch` renders snapshots; explicit one-shot
event dispatch is a future Unity integration change, not introduced by this spec.

## Ownership and changes

The structural source of truth is [catalog.json](../contracts/arena-v1/catalog.json)
and [arena.schema.json](../contracts/arena-v1/schemas/arena.schema.json).
Behavioral per-message notes are authored in
[semantics.md](../contracts/arena-v1/semantics.md); the common rules above are
hand-authored here. Everything inside the generated markers is derived from
those sources. Do not hand-edit generated tables. Examples are a reviewed,
versioned corpus, not automatically refreshed expected behavior.

For a change, update the catalog/schema, behavioral notes, examples and relevant
producer/consumer tests in the same PR. New addresses and variants require
coverage. These schemas describe the current emitted form and reject unknown
producer fields to catch accidental drift; they do not retroactively tighten
all historical deserializers. Required-field removal, type/casing/enum meaning,
ordering or replay-semantics changes need an explicit compatibility decision and
applicable protocol/schema/presentation version changes. Even an added optional
field needs a consumer compatibility review; it is not automatically safe for
strict decoders. Retain earlier execution versions for old recordings. Never
rewrite frozen reference fixtures to make a changed implementation pass.

```sh
python3 -m venv .tmp/contracts-venv
.tmp/contracts-venv/bin/pip install -r tools/requirements-contracts.txt
python3 tools/arena_contracts.py generate
.tmp/contracts-venv/bin/python tools/arena_contracts.py check
# After tools/setup.py, capture real inputs, outputs and inspection snapshots:
KITU_ARENA_CONTRACT_TRACE="$PWD/.tmp/arena-contract-trace.ndjson" \
  python3 tools/run.py cargo test --locked -p kitu-demo-game --test arena_contract
.tmp/contracts-venv/bin/python tools/arena_contracts.py check \
  --trace .tmp/arena-contract-trace.ndjson
```

CI checks schema validity, all example variants, unregistered literal addresses,
generated-document drift and every message in the real Rust trace. The trace
covers preparation, an eleven-floor run/death/retry, staged sources and a late
script fault. Existing combat/timeline tests cover timing and ordering; schemas
alone cannot prove those semantics. Unity wire-codec tests remain a separate
cross-language gate; this change does not generate C# receivers or run Unity.

