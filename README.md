# ♟️ Online Chess Game (Local & Online)

This project is a fully functional chess game that can be played locally against an engine (built using alpha-beta pruning algorithm) or online against another player. It represents a complete journey from implementing correct chess rules to building a multithreaded, networked application.

## ⚠️ Security Notice

The online mode was designed for learning purposes and is intended to be used **only within a trusted local network (LAN)**.

It does **not** implement encryption, authentication, or advanced security protections. Because of that, exposing the server to the public internet may result in security vulnerabilities.

For safety reasons, please avoid port-forwarding or hosting the server on public networks unless you add proper security mechanisms (such as TLS encryption and authentication).

## Project Journey

The first major challenge was ensuring correct move generation. The engine had to generate all legal moves while excluding illegal ones, and moves needed to be applied and undone consistently. This step was fundamental, as every other part of the project depends on a reliable move system.

Once correctness was achieved, performance became the main concern. Several optimizations and refactorings were necessary to make the engine efficient enough for real gameplay. This phase focused on reducing unnecessary computations and structuring the engine logic cleanly.

After the engine reached a usable level of performance, the project moved on to concurrency. Multithreading was introduced to allow the engine to think without freezing the user interface. This required learning how to safely coordinate threads and manage their lifecycle.

The final major step was implementing online play. This involved working with sockets, client–server communication, message synchronization, and connection handling. The result is an online mode where two players can play a complete chess match in real time over the network.

## Features

- Local play versus a chess engine  
- Online multiplayer using a client–server model (LAN only)  
- Correct legal move generation with undo support  
- Multithreaded engine execution  
- Real-time graphical interface  
- Clear separation between engine, UI, and networking  

## Conclusion

This project is both a playable chess game and a learning experience covering chess logic, engine optimization, multithreading, and network programming. It represents an end-to-end implementation of a complete chess system, from rules and move generation to real-time online play within a local network environment.
