# Set up Schrödinger before the workshop

**Do this before Day 2.** Installing and licensing takes longer than you expect, and the workshop starts with structures already on screen.

You need three things: the KU VPN, the Schrödinger software, and a licence pointing at the university server.

## 1. Connect to the KU VPN

The licence server only answers from inside the university network. Install the KU VPN client from the [KU IT self-service pages](https://kunet.ku.dk) and sign in with your KU credentials.

Stay connected to the VPN whenever you run Maestro, including during the workshop. If jobs suddenly fail to start, check the VPN first.

## 2. Install Maestro

You will receive a download link with installers for macOS, Linux and Windows. Install the full Schrödinger suite, not only Maestro, so that Protein Preparation, LigPrep and Glide are available.

## 3. Point it at the licence server

The licence address is the same on every platform:

```
53001@ilflic02fl.unicph.domain
```

### macOS

Open the Schrödinger **Configuration** app and enter the licence address.

![The Schrödinger configuration application on macOS](assets/setup-mac-configuration.png)

### Windows

Open the configuration tool and enter the same address.

![Entering the licence server address on Windows](assets/setup-windows-license-address.png)

![Schrödinger configuration on Windows](assets/setup-windows-configuration.png)

### Linux

Add the licence to your shell profile, for example in `~/.bashrc`:

```bash
export SCHROD_LICENSE_FILE="53001@ilflic02fl.unicph.domain"
```

Open a new terminal, or run `source ~/.bashrc`, for the change to take effect.

## Check that it works

- [ ] The VPN is connected.
- [ ] Maestro opens without a licence warning.
- [ ] **TASKS** finds *Protein Preparation Workflow*, *LigPrep* and *Ligand Docking*.

> **Still stuck?** Bring your laptop to the start of the session and ask an instructor. Do not spend the workshop fighting the installer — we have checkpoint files and spare machines.
> {: .warn }

[Workshop home](index.md) · [Maestro basics](maestro-basics.md)
