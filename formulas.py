import math
G = 6.674e-11  # Newtonian constant of gravitation (m^3 kg^-1 s^-2)
c = 3.0e8    # Speed of light (m/s)
M_sun = 1.989e30 # Solar mass (kg)
H0_default = 70.0 # Default Hubble constant (km/s/Mpc) - note units for Hubble's law function
pc = 3.08567758e16 # Parsec (m)
Mpc = pc * 1e6 # Megaparsec (m)
def _stefan_boltzmann(T, emissivity=1.0):
    STEFAN_BOLTZMANN_CONSTANT = 5.670374419e-8
    """
    Calculate the radiated power per unit area using the Stefan–Boltzmann law.
    
    Parameters:
        T (float): Temperature in Kelvin
        emissivity (float): Emissivity of the object (1.0 = perfect blackbody)
    
    Returns:
        float: Radiated power in W/m²
    """
    return emissivity * STEFAN_BOLTZMANN_CONSTANT * (T ** 4)

def stefan_boltzmann(args=[]):
    temp = input("Temperature in Kelvin [number]: ")
    try:
        temp = float(temp)
    except Exception as e:
        print("Error:", e)
        return

    emissivity = input("Emissivity (1 = blackbody, default 1) [0-1]: ")
    if not emissivity:
        emissivity = 1
    float(emissivity)

    print("Radiated Power:", str(_stefan_boltzmann(temp, emissivity)), "W/m^2")

def distance_modulus(m=None, M=None, d=None):
    """
    Calculate distance modulus relationships between apparent magnitude (m),
    absolute magnitude (M), and distance (d) in parsecs.
    
    You must provide two of the three parameters.
    
    Returns:
        float: The missing value (distance in parsecs, or a magnitude)
    """
    if m is not None and M is not None and d is None:
        # Solve for distance
        return 10 ** ((m - M + 5) / 5)
    elif m is not None and d is not None and M is None:
        # Solve for absolute magnitude
        return m - 5 * math.log10(d) + 5
    elif M is not None and d is not None and m is None:
        # Solve for apparent magnitude
        return M + 5 * math.log10(d) - 5
    else:
        raise ValueError("Provide exactly two of: m, M, and d (in parsecs).")
        
def schwarzschild_radius(mass):
    """
    Calculates the Schwarzschild radius for a given mass.

    Args:
        mass (float): The mass of the object (in kg).

    Returns:
        float: The Schwarzschild radius (in meters).
    """
    """ !!!!ADD CONSTANTS AS VARIABLES, G IS 6.674e-11!!!!"""
    return 2 * G * mass / c**2

def orbital_period_kepler(semimajor_axis, m1, m2):
    """
    Calculates the orbital period using Newton's form of Kepler's Third Law.

    Args:
        semimajor_axis (float): The semi-major axis of the orbit (in meters).
        m1 (float): Mass of the first object (in kg).
        m2 (float): Mass of the second object (in kg).

    Returns:
        float: The orbital period (in seconds).
    """
    # P^2 = (4 * pi^2 * a^3) / (G * (m1 + m2))
    period_squared = (4 * math.pi**2 * semimajor_axis**3) / (G * (m1 + m2))
    return math.sqrt(period_squared)

def calculate_redshift_z(observed_wavelength, rest_wavelength):
    """
    Calculates the relativistic redshift parameter (z).
    Wavelengths must be in the same unit (e.g., meters, Angstroms, nm).
    """
    z = (observed_wavelength - rest_wavelength) / rest_wavelength
    return z

def calculate_velocity_from_redshift(z):
    """
    Calculates the velocity (v) from the redshift parameter (z) using 
    the relativistic formula. Velocity is in meters per second (m/s).
    """
    # Formula: v = c * (((1+z)^2 - 1) / ((1+z)^2 + 1))
    v = c * (((1 + z)**2 - 1) / ((1 + z)**2 + 1))
    return v
def calculate_vis_viva_velocity(distance_r, semi_major_axis_a, central_mass_M):
    """
    Calculates the orbital velocity (v) using the Vis-viva equation.
    Uses SI units:
    distance_r (meters), semi_major_axis_a (meters), 
    central_mass_M (kilograms).
    Returns velocity in meters per second (m/s).
    """
    # Formula: v^2 = GM * (2/r - 1/a)
    # v = sqrt(GM * (2/r - 1/a))
    v_squared = G * central_mass_M * ((2 / distance_r) - (1 / semi_major_axis_a))
    if v_squared < 0:
        # This condition usually implies an unbound (hyperbolic) orbit, 
        # or incorrect input values for a bound orbit.
        raise ValueError("Calculation resulted in a negative v^2. Check input parameters for a bound orbit.")
        
    v = math.sqrt(v_squared)
    return v

def calculate_flux(luminosity_L, distance_d):
    """
    Calculates apparent flux (F) given luminosity (L) and distance (d).
    Luminosity must be in Watts (W), distance in meters (m).
    Returns flux in Watts per square meter (W/m^2).
    """
    # Formula: F = L / (4 * pi * d^2)
    flux = luminosity_L / (4 * math.pi * distance_d**2)
    return flux

def calculate_luminosity(flux_F, distance_d):
    """
    Calculates intrinsic luminosity (L) given apparent flux (F) and distance (d).
    Flux in W/m^2, distance in meters (m).
    Returns luminosity in Watts (W).
    """
    # Formula: L = F * (4 * pi * d^2)
    luminosity = flux_F * (4 * math.pi * distance_d**2)
    return luminosity

def calculate_distance(flux_F, luminosity_L):
    """
    Calculates distance (d) given apparent flux (F) and luminosity (L).
    Flux in W/m^2, luminosity in Watts (W).
    Returns distance in meters (m).
    """
    # Formula: d = sqrt(L / (4 * pi * F))
    if flux_F <= 0:
        raise ValueError("Flux must be positive to calculate a valid distance.")
        
    distance = math.sqrt(luminosity_L / (4 * math.pi * flux_F))
    return distance

def roche_lobe_distance(R, rho_primary, rho_object):
    """
    Calculate the Roche-lobe distance.
    
    Parameters:
        R (float): Radius of the primary body (in same length units you want d returned in)
        rho_primary (float): Density of the primary body
        rho_object (float): Density of the orbiting object
        
    Returns:
        float: Roche-lobe distance d
    """
    return 2.4 * R * (rho_primary / rho_object) ** (1/3)

exports = {
    "stefan_boltzmann": {
        "cb": stefan_boltzmann,
        "desc": "Calculate the radiated power per unit area using the Stefan–Boltzmann law",
        "aliases": ["stefanboltzman", "boltzman", "radiationpower", "blackbody"],
    }
}
