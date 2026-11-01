"""
Asset Generator module:
Generates 100% local, self-contained SVG vectors for suspect avatars,
location icons, murder weapon icons, noir header banners, and rubber stamps.
No external network calls or image downloads required.
"""
from typing import Dict


def get_suspect_avatar_svg(name: str, width: int = 120, height: int = 150) -> str:
    """Returns a stylish noir silhouette avatar SVG for each suspect."""
    avatars = {
        "Ravi": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 200" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad_ravi" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4A1517"/>
                    <stop offset="100%" stop-color="#1A0A0B"/>
                </linearGradient>
                <radialGradient id="glow_ravi" cx="50%" cy="40%" r="50%">
                    <stop offset="0%" stop-color="#E63946" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#E63946" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="160" height="200" rx="10" fill="url(#grad_ravi)" stroke="#E63946" stroke-width="2"/>
            <circle cx="80" cy="70" r="55" fill="url(#glow_ravi)"/>
            <!-- Silhouette Head & Shoulders -->
            <path d="M 30 190 C 30 145, 50 135, 65 130 C 65 110, 60 95, 60 75 C 60 50, 70 38, 80 38 C 90 38, 100 50, 100 75 C 100 95, 95 110, 95 130 C 110 135, 130 145, 130 190 Z" fill="#0D0E12"/>
            <!-- Fedora Hat -->
            <path d="M 45 52 C 55 35, 105 35, 115 52 Z" fill="#1C1E24"/>
            <ellipse cx="80" cy="52" rx="42" ry="7" fill="#2E333D"/>
            <rect x="58" y="46" width="44" height="4" fill="#E63946"/>
            <!-- Monocle & Chain -->
            <circle cx="88" cy="74" r="8" fill="none" stroke="#D4AF37" stroke-width="1.5"/>
            <path d="M 96 74 Q 105 85, 108 105" fill="none" stroke="#D4AF37" stroke-width="1" stroke-dasharray="2,2"/>
            <!-- Mustache -->
            <path d="M 72 87 Q 80 83, 88 87 Q 80 91, 72 87 Z" fill="#3D4451"/>
            <!-- Name Plaque -->
            <rect x="15" y="165" width="130" height="24" rx="4" fill="#14171E" stroke="#D4AF37" stroke-width="1"/>
            <text x="80" y="181" font-family="'Cinzel', serif, Georgia" font-size="12" font-weight="bold" fill="#F4F1EA" text-anchor="middle" letter-spacing="1.5">RAVI</text>
        </svg>
        """,
        "Meera": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 200" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad_meera" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#132A3E"/>
                    <stop offset="100%" stop-color="#0A141E"/>
                </linearGradient>
                <radialGradient id="glow_meera" cx="50%" cy="40%" r="50%">
                    <stop offset="0%" stop-color="#457B9D" stop-opacity="0.35"/>
                    <stop offset="100%" stop-color="#457B9D" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="160" height="200" rx="10" fill="url(#grad_meera)" stroke="#457B9D" stroke-width="2"/>
            <circle cx="80" cy="70" r="55" fill="url(#glow_meera)"/>
            <!-- Hair & Silhouette -->
            <circle cx="80" cy="70" r="28" fill="#0A0C10"/>
            <ellipse cx="60" cy="75" rx="12" ry="18" fill="#0A0C10"/>
            <ellipse cx="100" cy="75" rx="12" ry="18" fill="#0A0C10"/>
            <!-- Coat & Torso -->
            <path d="M 32 190 C 32 145, 52 135, 66 128 C 66 112, 63 98, 63 78 C 63 55, 71 45, 80 45 C 89 45, 97 55, 97 78 C 97 98, 94 112, 94 128 C 108 135, 128 145, 128 190 Z" fill="#0A0C10"/>
            <!-- Laboratory Spectacles -->
            <circle cx="72" cy="73" r="7" fill="none" stroke="#A8DADC" stroke-width="1.8"/>
            <circle cx="88" cy="73" r="7" fill="none" stroke="#A8DADC" stroke-width="1.8"/>
            <line x1="79" y1="73" x2="81" y2="73" stroke="#A8DADC" stroke-width="1.8"/>
            <!-- Pearl Necklace -->
            <path d="M 68 128 Q 80 138, 92 128" fill="none" stroke="#F1FAEE" stroke-width="2.5" stroke-dasharray="3,3"/>
            <!-- Name Plaque -->
            <rect x="15" y="165" width="130" height="24" rx="4" fill="#14171E" stroke="#457B9D" stroke-width="1"/>
            <text x="80" y="181" font-family="'Cinzel', serif, Georgia" font-size="12" font-weight="bold" fill="#F4F1EA" text-anchor="middle" letter-spacing="1.5">MEERA</text>
        </svg>
        """,
        "Kabir": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 200" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad_kabir" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#3D3008"/>
                    <stop offset="100%" stop-color="#141103"/>
                </linearGradient>
                <radialGradient id="glow_kabir" cx="50%" cy="40%" r="50%">
                    <stop offset="0%" stop-color="#D4AF37" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#D4AF37" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="160" height="200" rx="10" fill="url(#grad_kabir)" stroke="#D4AF37" stroke-width="2"/>
            <circle cx="80" cy="70" r="55" fill="url(#glow_kabir)"/>
            <!-- Top Hat -->
            <rect x="58" y="24" width="44" height="34" rx="2" fill="#16171B"/>
            <ellipse cx="80" cy="58" rx="34" ry="6" fill="#23252E"/>
            <rect x="58" y="52" width="44" height="4" fill="#D4AF37"/>
            <!-- Silhouette Head & Shoulders -->
            <path d="M 28 190 C 28 145, 48 135, 65 128 C 65 110, 62 95, 62 76 C 62 60, 70 56, 80 56 C 90 56, 98 60, 98 76 C 98 95, 95 110, 95 128 C 112 135, 132 145, 132 190 Z" fill="#0C0D11"/>
            <!-- Cigar & Smoke -->
            <rect x="85" y="86" width="16" height="3" transform="rotate(15, 85, 86)" fill="#8D5B4C"/>
            <circle cx="101" cy="90" r="1.5" fill="#E63946"/>
            <path d="M 103 89 Q 110 80, 107 72 Q 104 65, 112 58" fill="none" stroke="#CCCCCC" stroke-width="1.2" opacity="0.6"/>
            <!-- Name Plaque -->
            <rect x="15" y="165" width="130" height="24" rx="4" fill="#14171E" stroke="#D4AF37" stroke-width="1"/>
            <text x="80" y="181" font-family="'Cinzel', serif, Georgia" font-size="12" font-weight="bold" fill="#F4F1EA" text-anchor="middle" letter-spacing="1.5">KABIR</text>
        </svg>
        """,
        "Zara": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 200" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad_zara" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#2D114D"/>
                    <stop offset="100%" stop-color="#120621"/>
                </linearGradient>
                <radialGradient id="glow_zara" cx="50%" cy="40%" r="50%">
                    <stop offset="0%" stop-color="#8338EC" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#8338EC" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="160" height="200" rx="10" fill="url(#grad_zara)" stroke="#8338EC" stroke-width="2"/>
            <circle cx="80" cy="70" r="55" fill="url(#glow_zara)"/>
            <!-- Silhouette Head & Flowing Hair -->
            <path d="M 52 65 C 52 40, 108 40, 108 65 C 108 90, 114 125, 112 145 C 98 135, 62 135, 48 145 C 46 125, 52 90, 52 65 Z" fill="#0F0818"/>
            <path d="M 30 190 C 30 145, 50 135, 65 128 C 65 110, 63 95, 63 75 C 63 52, 71 45, 80 45 C 89 45, 97 52, 97 75 C 97 95, 95 110, 95 128 C 110 135, 130 145, 130 190 Z" fill="#07040B"/>
            <!-- Feather Hair Ornament -->
            <path d="M 60 55 Q 45 40, 42 25 Q 52 35, 58 48 Z" fill="#C77DFF"/>
            <!-- Mask / Veil Accent -->
            <path d="M 68 70 Q 80 75, 92 70" fill="none" stroke="#E0AAFF" stroke-width="1.5" stroke-dasharray="2,2"/>
            <!-- Name Plaque -->
            <rect x="15" y="165" width="130" height="24" rx="4" fill="#14171E" stroke="#8338EC" stroke-width="1"/>
            <text x="80" y="181" font-family="'Cinzel', serif, Georgia" font-size="12" font-weight="bold" fill="#F4F1EA" text-anchor="middle" letter-spacing="1.5">ZARA</text>
        </svg>
        """,
        "Dev": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 200" width="{width}" height="{height}">
            <defs>
                <linearGradient id="grad_dev" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#103630"/>
                    <stop offset="100%" stop-color="#051714"/>
                </linearGradient>
                <radialGradient id="glow_dev" cx="50%" cy="40%" r="50%">
                    <stop offset="0%" stop-color="#2A9D8F" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#2A9D8F" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <rect width="160" height="200" rx="10" fill="url(#grad_dev)" stroke="#2A9D8F" stroke-width="2"/>
            <circle cx="80" cy="70" r="55" fill="url(#glow_dev)"/>
            <!-- Silhouette Head & Shoulders -->
            <path d="M 32 190 C 32 145, 50 135, 66 128 C 66 108, 62 92, 62 72 C 62 50, 70 42, 80 42 C 90 42, 98 50, 98 72 C 98 92, 94 108, 94 128 C 110 135, 128 145, 128 190 Z" fill="#081110"/>
            <!-- Wing Collar & Bowtie -->
            <polygon points="74,130 86,130 80,137" fill="#E9ECEF"/>
            <polygon points="72,135 88,141 88,135 72,141" fill="#E76F51"/>
            <circle cx="80" cy="138" r="2.5" fill="#264653"/>
            <!-- Pocket Watch Chain -->
            <path d="M 68 155 Q 80 165, 92 155" fill="none" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Name Plaque -->
            <rect x="15" y="165" width="130" height="24" rx="4" fill="#14171E" stroke="#2A9D8F" stroke-width="1"/>
            <text x="80" y="181" font-family="'Cinzel', serif, Georgia" font-size="12" font-weight="bold" fill="#F4F1EA" text-anchor="middle" letter-spacing="1.5">DEV</text>
        </svg>
        """
    }
    return avatars.get(name, avatars["Ravi"]).strip()


def get_location_icon_svg(name: str, size: int = 56) -> str:
    """Returns vector SVG artwork for each crime location."""
    icons = {
        "Library": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Stack of books -->
            <path d="M 14 48 L 50 48 L 48 42 L 12 42 Z" fill="#9E2A2B"/>
            <path d="M 12 42 L 52 42 L 50 36 L 10 36 Z" fill="#3D5A80"/>
            <path d="M 16 36 L 48 36 L 46 30 L 14 30 Z" fill="#D4AF37"/>
            <!-- Open manuscript -->
            <path d="M 18 24 Q 32 20, 32 28 Q 32 20, 46 24 L 46 16 Q 32 12, 32 18 Q 32 12, 18 16 Z" fill="#F4F1EA"/>
            <line x1="32" y1="18" x2="32" y2="28" stroke="#333" stroke-width="1.5"/>
        </svg>
        """,
        "Kitchen": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Hanging Cleaver -->
            <path d="M 20 16 L 34 16 L 34 32 C 34 36, 20 36, 20 32 Z" fill="#ADB5BD"/>
            <rect x="25" y="8" width="4" height="8" rx="1" fill="#6C584C"/>
            <!-- Cauldron / Pot -->
            <ellipse cx="44" cy="40" rx="12" ry="4" fill="#343A40"/>
            <path d="M 32 40 C 32 50, 56 50, 56 40 Z" fill="#212529"/>
            <path d="M 40 32 Q 44 26, 42 22" fill="none" stroke="#E9ECEF" stroke-width="1.5" stroke-dasharray="2,2"/>
        </svg>
        """,
        "Garden": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Thorny Rose -->
            <circle cx="32" cy="24" r="10" fill="#E63946"/>
            <circle cx="32" cy="24" r="6" fill="#9E2A2B"/>
            <circle cx="32" cy="24" r="2.5" fill="#540B0E"/>
            <!-- Stem & Leaves -->
            <path d="M 32 34 Q 30 46, 36 54" fill="none" stroke="#2D6A4F" stroke-width="2.5"/>
            <path d="M 31 40 Q 24 38, 22 42 Q 27 46, 31 42" fill="#52B788"/>
            <path d="M 33 46 Q 42 44, 44 48 Q 39 52, 34 48" fill="#52B788"/>
        </svg>
        """,
        "Study": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Roll-top desk & banker lamp -->
            <rect x="12" y="38" width="40" height="16" rx="2" fill="#4A3525"/>
            <rect x="18" y="24" width="14" height="6" rx="3" fill="#2D6A4F"/>
            <path d="M 25 30 L 25 38" stroke="#D4AF37" stroke-width="2"/>
            <circle cx="25" cy="38" r="4" fill="#D4AF37"/>
            <!-- Feather Quill -->
            <path d="M 40 40 Q 48 30, 48 18 Q 44 26, 38 38 Z" fill="#F4F1EA"/>
        </svg>
        """,
        "Ballroom": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Chandelier -->
            <line x1="32" y1="10" x2="32" y2="22" stroke="#D4AF37" stroke-width="2"/>
            <path d="M 18 26 Q 32 34, 46 26" fill="none" stroke="#D4AF37" stroke-width="2.5"/>
            <circle cx="18" cy="24" r="3" fill="#FFF3B0"/>
            <circle cx="32" cy="27" r="3" fill="#FFF3B0"/>
            <circle cx="46" cy="24" r="3" fill="#FFF3B0"/>
            <!-- Venetian Mask -->
            <path d="M 22 46 C 22 38, 42 38, 42 46 C 36 50, 28 50, 22 46 Z" fill="#8338EC"/>
            <circle cx="28" cy="44" r="2.5" fill="#F4F1EA"/>
            <circle cx="36" cy="44" r="2.5" fill="#F4F1EA"/>
        </svg>
        """
    }
    return icons.get(name, icons["Library"]).strip()


def get_weapon_icon_svg(name: str, size: int = 56) -> str:
    """Returns vector SVG artwork for each murder weapon."""
    icons = {
        "Knife": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#E63946" stroke-width="1.5"/>
            <!-- Dagger Blade -->
            <path d="M 18 46 L 42 16 Q 48 22, 44 28 L 22 50 Z" fill="#CED4DA"/>
            <line x1="20" y1="48" x2="43" y2="22" stroke="#FFFFFF" stroke-width="1.5"/>
            <!-- Guard & Handle -->
            <rect x="14" y="48" width="16" height="4" transform="rotate(-45, 14, 48)" fill="#D4AF37"/>
            <line x1="16" y1="50" x2="10" y2="56" stroke="#540B0E" stroke-width="5" stroke-linecap="round"/>
        </svg>
        """,
        "Candlestick": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Brass Candlestick -->
            <ellipse cx="32" cy="52" rx="14" ry="4" fill="#B78A10"/>
            <path d="M 29 52 L 29 28 L 35 28 L 35 52 Z" fill="#D4AF37"/>
            <rect x="26" y="24" width="12" height="4" rx="1" fill="#F3C649"/>
            <!-- Candle & Flame -->
            <rect x="29" y="14" width="6" height="10" fill="#F8F9FA"/>
            <path d="M 32 6 Q 36 10, 32 14 Q 28 10, 32 6 Z" fill="#FF9E00"/>
        </svg>
        """,
        "Poison": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#457B9D" stroke-width="1.5"/>
            <!-- Poison Bottle -->
            <rect x="28" y="10" width="8" height="6" fill="#D4AF37"/>
            <rect x="24" y="16" width="16" height="32" rx="4" fill="#03045E"/>
            <rect x="26" y="26" width="12" height="20" rx="2" fill="#0077B6"/>
            <!-- Skull indicator -->
            <circle cx="32" cy="34" r="3.5" fill="#E9ECEF"/>
            <line x1="30" y1="39" x2="34" y2="39" stroke="#E9ECEF" stroke-width="1.5"/>
            <!-- Bubbles -->
            <circle cx="30" cy="22" r="1.5" fill="#90E0EF"/>
            <circle cx="34" cy="20" r="1" fill="#90E0EF"/>
        </svg>
        """,
        "Rope": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#D4AF37" stroke-width="1.5"/>
            <!-- Coiled Hemp Rope -->
            <ellipse cx="32" cy="38" rx="18" ry="10" fill="none" stroke="#BC6C25" stroke-width="3.5" stroke-dasharray="4,2"/>
            <ellipse cx="32" cy="34" rx="16" ry="8" fill="none" stroke="#DDA15E" stroke-width="3.5" stroke-dasharray="4,2"/>
            <path d="M 32 26 L 32 10" stroke="#BC6C25" stroke-width="3" stroke-dasharray="3,2"/>
            <!-- Loop -->
            <circle cx="32" cy="18" r="5" fill="none" stroke="#DDA15E" stroke-width="2.5"/>
        </svg>
        """,
        "Revolver": f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}">
            <rect width="64" height="64" rx="8" fill="#1A1C23" stroke="#E63946" stroke-width="1.5"/>
            <!-- Barrel & Cylinder -->
            <rect x="14" y="24" width="22" height="6" fill="#6C757D"/>
            <rect x="36" y="21" width="12" height="12" rx="2" fill="#495057"/>
            <!-- Grip -->
            <path d="M 44 28 L 52 48 C 50 52, 44 52, 42 46 L 38 32 Z" fill="#6C584C"/>
            <!-- Trigger & Guard -->
            <path d="M 36 33 Q 32 40, 40 40" fill="none" stroke="#ADB5BD" stroke-width="1.5"/>
            <line x1="37" y1="33" x2="36" y2="37" stroke="#343A40" stroke-width="1.5"/>
        </svg>
        """
    }
    return icons.get(name, icons["Knife"]).strip()





def get_case_solved_stamp_svg() -> str:
    """Returns an authentic vintage red rubber stamp badge for 'CASE SOLVED'."""
    return """
    <div style="display: flex; justify-content: center; margin: 20px 0;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 120" width="300" height="110" style="transform: rotate(-10deg);">
            <!-- Outer weathered rectangular border -->
            <rect x="10" y="10" width="300" height="100" rx="10" fill="none" stroke="#E63946" stroke-width="5" stroke-dasharray="18,3,8,2" opacity="0.9"/>
            <rect x="18" y="18" width="284" height="84" rx="6" fill="none" stroke="#E63946" stroke-width="2" opacity="0.8"/>
            <!-- Text -->
            <text x="160" y="64" font-family="'Impact', 'Cinzel', sans-serif" font-size="34" font-weight="900" fill="#E63946" text-anchor="middle" letter-spacing="5" opacity="0.95">CASE SOLVED</text>
            <text x="160" y="88" font-family="'Courier New', monospace" font-size="12" font-weight="bold" fill="#E63946" text-anchor="middle" letter-spacing="3" opacity="0.85">PROVED BY RESOLUTION</text>
            <!-- Stamp Stars -->
            <polygon points="40,55 43,62 50,62 44,66 46,73 40,69 34,73 36,66 30,62 37,62" fill="#E63946" opacity="0.85"/>
            <polygon points="280,55 283,62 290,62 284,66 286,73 280,69 274,73 276,66 270,62 277,62" fill="#E63946" opacity="0.85"/>
        </svg>
    </div>
    """.strip()
