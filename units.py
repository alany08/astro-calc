import re
import math

def convert_and_print(args=[]):
    if len(args) != 1:
        print("Error: please provide an argument for what you want to convert")
        print("For example: `convert 23kg`")
        return
    try:
        _convert_and_print(args[0])
    except Exception as e:
        print("Error:", e)

def _convert_and_print(qty_str):
    """
    Takes a single quantity like "312N", "123kg", "2.5km", "100ms", "1AU", "1pc", "10Myr", "1eV"
    and prints equivalent values in common units for the same dimension,
    truncated to 4 decimal places.
    """

    qty_str = qty_str.strip().replace('µ', 'u').replace('μ', 'u')

    # Map unit -> (dimension, to_SI_factor)
    # SI factor means: value_in_SI = value * to_SI_factor, where SI base is:
    #  - mass: kg
    #  - force: N
    #  - length: m
    #  - time: s
    #  - energy: J
    #  - angle: rad
    #  - freq: Hz
    units = {
        # Mass
        'kg': ('mass', 1.0),
        'g':  ('mass', 1e-3),
        'lb': ('mass', 0.45359237),
        'oz': ('mass', 0.028349523125),
        # Astronomy mass
        'Msun':   ('mass', 1.98847e30),  # solar mass
        'Mjup':   ('mass', 1.89813e27),  # Jupiter mass
        'Mearth': ('mass', 5.9722e24),   # Earth mass

        # Force
        'N':   ('force', 1.0),
        'lbf': ('force', 4.4482216152605),
        'kgf': ('force', 9.80665),

        # Length
        'm':  ('length', 1.0),
        'cm': ('length', 0.01),
        'mm': ('length', 0.001),
        'km': ('length', 1000.0),
        'in': ('length', 0.0254),
        'ft': ('length', 0.3048),
        'yd': ('length', 0.9144),
        'mi': ('length', 1609.344),
        # Astronomy length
        'AU': ('length', 149_597_870_700.0),          # astronomical unit (exact)
        'ly': ('length', 9.4607304725808e15),         # light-year (Julian)
        'pc': ('length', 3.085677581491367e16),       # parsec
        # kpc, Mpc via prefixes

        # Time
        's':   ('time', 1.0),
        'min': ('time', 60.0),
        'h':   ('time', 3600.0),
        # Astronomy time
        'day': ('time', 86400.0),
        'yr':  ('time', 31557600.0),  # Julian year

        # Energy (astronomy-friendly)
        'J':   ('energy', 1.0),
        'erg': ('energy', 1e-7),                 # cgs
        'eV':  ('energy', 1.602176634e-19),      # exact

        # Angle (astronomy)
        'rad':    ('angle', 1.0),
        'deg':    ('angle', math.pi / 180.0),
        'arcmin': ('angle', math.pi / (180.0 * 60.0)),
        'arcsec': ('angle', math.pi / (180.0 * 3600.0)),
        'mas':    ('angle', math.pi / (180.0 * 3600.0 * 1e3)),
        'uas':    ('angle', math.pi / (180.0 * 3600.0 * 1e6)),

        # Frequency (astronomy)
        'Hz':  ('freq', 1.0),
        # kHz, MHz, GHz via prefixes
    }

    # SI prefixes (subset; upper- and lower-case where appropriate)
    prefixes = {
        'da': 1e1,   # deca
        'k':  1e3,
        'M':  1e6,
        'G':  1e9,
        'T':  1e12,
        'm':  1e-3,
        'c':  1e-2,
        'd':  1e-1,
        'u':  1e-6,  # micro
        'n':  1e-9,
    }

    # Bases that accept prefixes
    prefixable_bases = {'g', 'm', 's', 'N', 'pc', 'yr', 'Hz', 'eV'}

    # Common synonyms (case-insensitive keys mapping to canonical unit keys)
    synonyms = {
        # Mass
        'lbs': 'lb',
        'pound': 'lb',
        'pounds': 'lb',
        'ounce': 'oz',
        'ounces': 'oz',
        'msun': 'Msun',
        'msol': 'Msun',
        'solarmass': 'Msun',
        'mjup': 'Mjup',
        'jupitermass': 'Mjup',
        'mearth': 'Mearth',
        'earthmass': 'Mearth',

        # Force
        'newton': 'N',
        'newtons': 'N',

        # Length
        'meter': 'm',
        'meters': 'm',
        'metre': 'm',
        'metres': 'm',
        'centimeter': 'cm',
        'centimeters': 'cm',
        'millimeter': 'mm',
        'millimeters': 'mm',
        'kilometer': 'km',
        'kilometers': 'km',
        'inch': 'in',
        'inches': 'in',
        'foot': 'ft',
        'feet': 'ft',
        'yard': 'yd',
        'yards': 'yd',
        'mile': 'mi',
        'miles': 'mi',
        'au': 'AU',
        'astronomicalunit': 'AU',
        'lightyear': 'ly',
        'lightyears': 'ly',
        'parsec': 'pc',
        'parsecs': 'pc',
        'kiloparsec': 'pc',  # will be handled via prefix if user inputs "kpc"
        'megaparsec': 'pc',  # same via "Mpc"

        # Time
        'sec': 's',
        'second': 's',
        'seconds': 's',
        'minute': 'min',
        'minutes': 'min',
        'hr': 'h',
        'hour': 'h',
        'hours': 'h',
        'd': 'day',
        'day': 'day',
        'days': 'day',
        'yr': 'yr',
        'year': 'yr',
        'years': 'yr',
        'julianyear': 'yr',

        # Energy
        'joule': 'J',
        'joules': 'J',
        'electronvolt': 'eV',
        'electronvolts': 'eV',
        'ergs': 'erg',

        # Angle
        'radian': 'rad',
        'radians': 'rad',
        'degree': 'deg',
        'degrees': 'deg',
        'arcminute': 'arcmin',
        'arcminutes': 'arcmin',
        'arcsecond': 'arcsec',
        'arcseconds': 'arcsec',

        # Frequency
        'hertz': 'Hz',
    }

    targets = {
        'mass':   ['kg', 'g', 'mg', 'lb', 'oz', 'Msun', 'Mjup', 'Mearth'],
        'force':  ['N', 'kN', 'lbf', 'kgf'],
        'length': ['m', 'km', 'AU', 'ly', 'pc', 'kpc', 'Mpc', 'in', 'ft', 'yd', 'mi'],
        'time':   ['s', 'ms', 'min', 'h', 'day', 'yr', 'kyr', 'Myr', 'Gyr'],
        'energy': ['J', 'erg', 'eV', 'keV', 'MeV', 'GeV', 'TeV'],
        'angle':  ['rad', 'deg', 'arcmin', 'arcsec', 'mas', 'uas'],
        'freq':   ['Hz', 'kHz', 'MHz', 'GHz'],
    }

    def resolve_unit(u):
        # Direct match (case-sensitive)
        if u in units:
            return units[u]
        # Synonyms (case-insensitive)
        u_low = u.lower()
        if u_low in synonyms:
            canon = synonyms[u_low]
            if canon in units:
                return units[canon]
        # Try prefix decomposition (longest prefix first)
        for pref in sorted(prefixes.keys(), key=len, reverse=True):
            if u.startswith(pref):
                base = u[len(pref):]
                base_canon = base if base in units else synonyms.get(base.lower(), base)
                if base_canon in units and base_canon in prefixable_bases:
                    dim, base_factor = units[base_canon]
                    return dim, base_factor * prefixes[pref]
        return None

    # Parse a single "number+unit" like "312N"
    m = re.match(r'^\s*([+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*([A-Za-z]+)\s*$', qty_str)
    if not m:
        raise ValueError(f"Could not parse quantity: {qty_str!r}")

    value = float(m.group(1))
    unit = m.group(2)
    resolved = resolve_unit(unit)
    if not resolved:
        raise ValueError(f"Unknown or unsupported unit: {unit!r}")

    dim, to_si = resolved
    value_si = value * to_si

    def fmt_sig4(x):
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "-inf" if x < 0 else "inf"
        if x == 0:
            return "0.000e+00"  # 4 sig figs: 1 leading + 3 decimals
        return f"{x:.3e}"       # 4 significant figures via e-format

    # Print equivalents
    print(f"Input: {qty_str}  ->  Dimension: {dim}")
    for tgt in targets.get(dim, []):
        tgt_resolved = resolve_unit(tgt)
        if not tgt_resolved:
            continue
        tgt_dim, tgt_to_si = tgt_resolved
        if tgt_dim != dim:
            continue
        val_in_tgt = value_si / tgt_to_si
        print(f"{tgt}: {fmt_sig4(val_in_tgt)}")

exports = {
    "convert_units": {
        "cb": convert_and_print,
        "desc": "Converts arbitrary units",
        "aliases": ["convert", "conv", "units"],
    }
}