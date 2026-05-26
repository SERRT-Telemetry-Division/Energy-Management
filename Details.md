__Physical Parameters & Constants__ 
$m$ (Mass of the vehicle and driver): kg 

$A$ (Frontal surface area): m² 

$A_{pv}$ (Solar array size): m² 

$C_d$ (Coefficient of aerodynamic drag): Dimensionless 

$C_r$ (Coefficient of rolling resistance): Dimensionless 

$\rho$ (Air density): kg/m³ 

$g$ (Gravitational acceleration): m/s² 

__Dynamic Environmental & State Variables__
$v_k$, $v_{k+1}$ (Vehicle speed at discrete intervals): m/s 

$v_w$ (Wind speed): m/s 

$\theta$ (Road inclination angle): radians 

$GHI_k$ (Global Horizontal Irradiance): W/m² 

$t_k$ (Real driving time between states): seconds 

$t_{acc}$ (Time over which acceleration occurs): seconds 

__Energy, Power, & Efficiencies__
$E_{cap}$ (Total battery storage capacity): Joules (J) 

$P_{aux}$ (Constant auxiliary electrical losses): Watts (W) 

$\eta_{motor}$ (Motor and controller efficiency): Dimensionless (Ratio) 

$\eta_{elec}$ (Combined solar/electrical efficiency): Dimensionless (Ratio) 

$\alpha_{day(x)}$ (Required energy at the start of the day): % (Percentage) 

$SoC_{day(x)}$ (State of Charge of the battery): % (Percentage) 

__Crucial note on battery capacity__: The research paper lists the battery storage capacity ($E_{cap}$) as 17.8 MJ or 4942 Wh. For your Python script, it is highly recommended to convert this directly into standard Joules (17,800,000 J) in your constants file. This ensures that when you calculate Watts over time (seconds), the resulting energy mathematically aligns with your battery capacity without requiring constant inline conversions.

__Calculated Outputs__

When your Python script computes the final equations, the resulting units will be:Forces ($F_1$, $F_2$, $F_3$, $F_{acc}$): Newtons (N) Power ($P_{loss}$, $P_{sun}$, $P_{batt}$, $P_{acc}$): Watts (W) Energy ($E_{acc}$): Joules (J) 