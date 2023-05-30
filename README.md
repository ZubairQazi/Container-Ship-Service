# Container Ship Loading & Unloading

## Overview

Welcome to our senior design project for CS179M (AI) at UCR! This Flask-based web application provides dockyard crane operators with a simple and powerful tool to determine the optimal unloading and loading paths for container ships.

## Key Features

1. **Efficient Path Calculation:**  Leveraging the A* algorithm, this application ensures highly efficient path calculation for container ship unloading and loading. A* combines the power of heuristic search and graph traversal, guaranteeing optimal solutions by efficiently exploring the search space. By intelligently leveraging this algorithm, our software engineering-driven solution significantly reduces computational complexity, allowing crane operators to obtain the most efficient paths with speed and accuracy.

2. **Interactive User Interface:** This application provides crane operators with a simple yet effective user interface that describes each step of container movement during unloading and loading processes. Through an intuitive and visually appealing interface, operators can navigate through a colored grid diagram of the container ship, accompanied by the precise positioning of containers at each step. This visualization enables operators to grasp the optimal unloading and loading paths effortlessly.

3. **Robust Manifest Persistence and Recovery**: The application incorporates a robust feature that ensures the safety of your data, even in the face of system failures or other unforeseen circumstances. In the event of an unexpected shutdown or system crash, the application automatically saves the current manifest, preserving the progress made during loading/unloading. Upon rebooting, the application seamlessly recovers the previous state, allowing crane operators to resume operations from where they left off.

4. **Updated Manifest Delivery upon Completion**: Once the loading/unloading process is completed, the application provides operators with an updated manifest. This comprehensive report captures the final configuration of the container ship, detailing the optimized unloading and loading paths, container positions, and any relevant metrics or comments from the operator. The operator can directly send this manifest to their superior and/or to the ship crew.


## Installation

To get started with this project, follow these steps:

1. Clone the repository: `git clone https://github.com/ZubairQazi/CS179M.git`
2. Navigate to the project directory: `cd CS179M`
7. Run the application: ``flask --app app run`
8. Access the application in your web browser at `http://localhost:5000`.


## License

This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the application in accordance with the terms of the license.
