import { closeSync, openSync, writeSync } from "node:fs"
import { Plugin } from "@opencode/plugin/tui"

export default Plugin.define({
  id: "local.osc133",
  setup(ctx) {
    let tty
    try {
      tty = openSync("/dev/tty", "w")
    } catch {
      return
    }
    let active: string | undefined

    const finish = (sessionID: string) => {
      if (active !== sessionID) return
      writeSync(tty, "\x1b]133;D\x07")
      active = undefined
    }

    const stops = [
      ctx.data.on("session.execution.started", (event) => {
        const route = ctx.ui.router.current()
        if (route.type !== "session") return
        if (route.sessionID !== event.data.sessionID) return
        if (active) finish(active)
        active = event.data.sessionID
        writeSync(tty, "\x1b]133;C\x07")
      }),
      ctx.data.on("session.execution.succeeded", (event) => finish(event.data.sessionID)),
      ctx.data.on("session.execution.failed", (event) => finish(event.data.sessionID)),
      ctx.data.on("session.execution.interrupted", (event) => finish(event.data.sessionID)),
    ]

    return () => {
      stops.forEach((stop) => stop())
      if (active) finish(active)
      closeSync(tty)
    }
  },
})
