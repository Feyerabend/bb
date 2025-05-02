
## Checkpoints

Checkpoints absolutely play an important role in both installation procedures and
interrupted file transfers today, though they've evolved and are sometimes called
by different *names* depending on the context.

### Installation Procedures

Modern installation systems heavily rely on checkpoint mechanisms to ensure reliability.
When you're installing an operating system or complex software package, the process
typically follows these steps:

  The installer first verifies system requirements and compatibility, creating an initial
  checkpoint. It then proceeds through various phases (copying files, configuring settings,
  updating registries), establishing checkpoints after completing each major phase. If the
  installation fails midway, the system can resume from the last successful checkpoint
  rather than starting over.

  Package managers like apt, yum, or Homebrew implement transaction-based installations
  with implicit checkpoints. They first calculate dependencies, download necessary packages,
  and then apply changes in a way that can be rolled back if problems occur.
  Windows Installer (MSI) technology similarly uses transaction-based installation with
  commit and rollback capabilities--essentially checkpoint mechanisms by another name.

### Interrupted File Transfers

File transfer protocols have incorporated checkpoint-like mechanisms for decades, especially
for large files or unreliable connections. These capabilities appear in several forms:

  Resume functionality in download managers and file transfer protocols allows interrupted
  transfers to continue from where they left off rather than restarting. This works because
  the system periodically records how many bytes have been successfully transferred--effectively
  creating checkpoints.

  Modern cloud storage services like Dropbox, Google Drive, or OneDrive use sophisticated
  file synchronisation algorithms that break files into chunks and track which chunks have
  been successfully uploaded or downloaded. This chunking approach is essentially a checkpoint
  system working at a finer granularity.

  BitTorrent and similar peer-to-peer protocols take this even further by dividing files
  into pieces that can be verified independently using hashes, allowing transfers to resume
  not just from network interruptions but also to recover from data corruption.

### Other Related Mechanisms

Several related mechanisms work alongside checkpoints in these scenarios:

Transaction logs keep records of operations to be performed, allowing systems to replay
operations after a failure. Database systems, file systems, and installation procedures
all use transaction logs to enhance reliability.

Journaling in modern file systems (like ext4, NTFS, or APFS) records pending changes
before committing them to disk. This isn't quite a checkpoint system, but serves a
similar purpose of maintaining system integrity during interruptions.

Delta synchronisation, used by backup and sync tools, identifies only the changed
portions of files rather than transferring entire files again. This works by keeping
track of file state at various points in time--conceptually similar to checkpoints.

Dirty bit tracking is used by many systems to mark portions of data that have been
modified but not yet saved to persistent storage. This simple mechanism helps systems
recover after crashes by identifying which parts need attention.

The concept of checkpoints has become so fundamental to reliable computing that it
appears in virtually all critical systems today, though often integrated into higher-level
abstractions like transactions, journaling, or synchronisation protocols. The central
idea--recording state at strategic points to enable recovery--remains consistent across
these varied implementations.

Bubenko, J. & Ohlin, T. (1970-1971). *Introduktion till operativsystem.* Lund: Studentlitt.