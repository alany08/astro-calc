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

exports = {
    "stefan_boltzmann": {
        "cb": stefan_boltzmann,
        "desc": "Calculate the radiated power per unit area using the Stefan–Boltzmann law",
        "aliases": ["stefanboltzman", "boltzman", "radiationpower", "blackbody"],
    }
}