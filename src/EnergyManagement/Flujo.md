#### High Level EMS Predictions Button's Backend Processes

- User presses the button "Get EMS predictions".
    - get_ems_predictions(VehicleConfig: car, EnvironmetState: weather, Map) -> Runs all EMS processes and returns the optimal speeds for each section of the race.
    - Args: 
        - car (VehicleConfig object): Dataclass object containing necessary car data
        - weather (EnvironmentState object): Dataclass object containing necessary weather data

    - Returns:
        Speeds (Array): A list of the speeds needed 

- On function call, function evaluates if the section of the race is curved or straight.
    - If section is curved:
        - Use specific function for calculating forces on turn sections.

    - Else if section is straight:
        - Use regular functions for calculating forces against the car.
    - Keep in mind, this will be stored in a boolean variable.

- Calculates rolling resistance and gravity (forces exerted against the car, given a certain speed $v_k$). 
    - We ignore aerodynamic drag for simplicity's sake.
    - The incline angle ($\theta$) is assumed to be 0% for the Formula Sun Grand Prix track in Minnesota. 

- These calculations are repeated multiple times when calling SciPy's minimize() function.
    - Goal of minimize(): to maximize $SoC$ when given an array of speeds by minimizing the output of $-SoC$.
    - Function varies speed parameters algorithmically to find the optimal solution.

- Additional logic that needs to be worked out:
    - Average speed calculation in curved sections of the track
    - Creating graphs for prediction data.
    - Gathering car data to compare it to predictions.



