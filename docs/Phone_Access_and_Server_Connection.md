# Fan research — phone access and server connection

Updated: October 21, 2026 (America/Los_Angeles).

## Current access

- This chat: Continue fan research (ID `01a15f7c-51a3-7231-8f58-93ac824783ba`).
- Lab: https://ionic-wind-virtual-lab.spokanelawncare.chatgpt.site
- Lab verified active through the Sites owner tools; access is restricted to the owner's account. Open it on a phone signed into the same account.
- Local project: `C:\Users\spoka\Documents\Codex\2026-10-21\lo`.
- Linux compute: user's mail VPS, SSH alias `mail`, host `207.180.232.228`, port 22, existing key-based root login. Strict host-key verification succeeded.
- Persistent fan files on mail: `/opt/fan-research/2026-10-21`.
- Connection from this computer: `ssh -o BatchMode=yes -o StrictHostKeyChecking=yes mail`.
- Fleet helper documented by local skills: `python C:\Users\spoka\.fleet\connect.py mail "<command>"`. The restricted sandbox blocked this helper's socket; native SSH succeeded with approved network access.
- Do not copy keys, passwords, tokens or credential files into this project or onto the phone.

## Phone-to-chat connection — confirmed by user

The user wants to continue the same chat and view the lab/results from the phone. The intended route is phone → authenticated Codex desktop connection → this laptop → mail over SSH. This does not require opening a public application-server port.

The official setup is Settings → Connections → Control this PC → Set up/Add, then scan the QR code with the phone and finish account verification. The user reports those controls are absent. The installed Windows package is `OpenAI.Codex_26.1013.4894.0`. `codex remote-control start --json` failed with: `codex app-server daemon lifecycle is only supported on Unix platforms`. No remote-control daemon or pairing was established by that command.

The user subsequently confirmed: "im now connected to this pc thru chatgpt app". Phone-to-PC access is established by that confirmation. The intended working route is now phone → this PC → existing SSH connection to mail. Keep the desktop app running and the laptop awake/online to continue this local chat remotely. VPS jobs themselves can run independently once launched there. If reconnecting later, use the same account and workspace.

The prior hosted Linux workspace is separate, temporary infrastructure; it is not an SSH endpoint available for this bridge. Existing cloud conversations do not automatically gain access to this computer merely because this project has an SSH connection.

## Sources

- Remote setup, SSH and host availability: https://learn.chatgpt.com/docs/remote-connections
- CLI remote-control behavior: https://learn.chatgpt.com/docs/cli/reference

## Research state

Recovered full prior brief: `outputs/Fanless_Fan_Project.md`. It preserves the original findings and labels the 80 browser scenarios as unvalidated arithmetic estimates. The private lab's notebook uses browser-local storage; export records to move them between devices. A live shared simulation backend has not been connected to the website.

Public solver pinned on mail: https://github.com/nzhtbyn/buoyantBoussinesqPimpleEHDFoam at commit `cfd66422bce0e17fa4b2ad0b622e37ad7a553fcd`.

Official runtime: `openfoam/openfoam4-paraview50:4.1`, image digest `sha256:a9cde0fffd6dee35f1d6fac0494d8595850aa8063005997a75c8430666f6c230`.

Solver built successfully in a network-disabled container limited to 2 CPUs and 4 GB RAM. A shortened startup case was launched; final outcome is recorded separately in the simulation report. Startup tests are not reproduction of the published heat-transfer comparison, nor validation of the proposed fan.
