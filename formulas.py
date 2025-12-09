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
    
exports = {
    "stefan_boltzmann": {
        "cb": stefan_boltzmann,
        "desc": "Calculate the radiated power per unit area using the Stefan–Boltzmann law",
        "aliases": ["stefanboltzman", "boltzman", "radiationpower", "blackbody"],
    }
}
