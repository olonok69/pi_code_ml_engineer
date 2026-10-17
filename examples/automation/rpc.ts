// RPC mode from TypeScript — the docs recommend RpcClient (exported by
// @earendil-works/pi-coding-agent) with promptAndWait() over hand-rolled JSONL.
//
// ⚠️ UNVERIFIED SHAPE: the course findings name RpcClient and promptAndWait() but do not record the
// constructor options or the return type. Check the [rpc] docs / the package's type definitions
// before relying on the lines marked VERIFY. Under the hood it drives `pi --mode rpc`: JSONL commands
// on stdin (prompt, steer, follow_up, abort, get_state, compact, set_model, …), responses and events
// on stdout. Extension dialogs are forwarded through the RPC extension-UI sub-protocol.
import { RpcClient } from "@earendil-works/pi-coding-agent";

const client = new RpcClient({ cwd: process.cwd() } as never); // VERIFY constructor options
const result = await client.promptAndWait("List the three largest files under src/ and why they are large.");
console.log(result); // VERIFY return shape
