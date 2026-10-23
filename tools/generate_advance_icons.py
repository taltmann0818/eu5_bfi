"""Distinct financial glyphs in the existing editable BFI SVG vocabulary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLD = '#d6b369'


def line(points, width=5):
    return f'<polyline points="{points}" fill="none" stroke="{GOLD}" stroke-width="{width}" stroke-linejoin="round"/>'


def box(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{GOLD}" stroke-width="5"/>'


def ring(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{GOLD}" stroke-width="5"/>'


def glyphs():
    return {
        'debt_restructuring': box(31, 25, 45, 69)+line('42,42 65,42 42,42 42,55 57,55')+line('58,82 73,67 84,78 73,89')+line('78,62 89,51 100,62 88,74'),
        'commercial_bills': box(29, 28, 57, 72)+line('41,45 72,45')+line('41,60 61,60')+line('56,91 97,30 102,39 65,95 56,91'),
        'commodity_investments': line('38,36 52,32 67,37 78,69 75,95 30,95 28,69 38,36')+line('38,47 62,47')+ring(87, 82, 15)+line('87,72 87,92'),
        'commenda': line('25,81 37,96 90,96 103,79 25,81')+line('62,27 62,79')+line('69,32 95,69 69,69 69,32')+line('54,40 33,71 54,71'),
        'corporate_credit': line('25,54 64,30 103,54 25,54')+box(32, 57, 64, 40)+line('43,65 43,88 60,88 60,65')+ring(89, 85, 16)+line('89,75 89,95'),
        'company_equity': ring(64, 64, 34)+line('64,30 64,98')+line('30,64 98,64')+ring(64, 64, 12),
        'bank_share_dealing': box(25, 26, 49, 61)+box(54, 49, 49, 53)+line('36,42 63,42')+line('36,55 48,55')+ring(78, 76, 12),
        'collateralization': box(35, 56, 58, 43)+line('45,54 45,38 53,28 75,28 83,38 83,54')+ring(64, 73, 6)+line('64,80 64,89'),
        'warehouse_receipts': line('23,49 62,28 101,49')+box(28, 51, 62, 44)+box(42, 64, 20, 31)+box(75, 63, 29, 39)+line('82,74 97,74')+line('82,85 97,85'),
        'commodity_forwards': box(26, 48, 49, 48)+line('26,48 50,34 75,48 50,63 26,48 50,63 50,96')+ring(87, 43, 18)+line('87,30 87,43 97,49'),
        'project_security': line('64,26 97,40 93,73 80,92 64,104 48,92 35,73 31,40 64,26')+ring(64, 48, 7)+line('64,55 64,84')+line('43,70 48,81 64,88 80,81 85,70')+line('53,63 75,63'),
        'sovereign_banknotes': box(24, 32, 69, 41)+box(35, 56, 69, 40)+ring(69, 76, 11)+line('34,45 45,45')+line('82,83 94,83'),
        'liquidity_facilities': line('30,98 98,98 98,83 30,83 30,98')+line('39,80 39,65 90,65 90,80')+line('49,61 49,47 81,47 81,61')+line('64,23 64,42')+line('52,32 64,43 76,32'),
        'advanced_clearing': line('34,42 89,42 78,30')+line('89,42 78,54')+line('89,58 89,89 101,78')+line('89,89 77,78')+line('73,89 39,89 50,101')+line('39,89 50,77')+line('39,73 39,42 27,53')+ring(64, 65, 9),
        'margining_and_risk_management': line('64,28 64,96')+line('34,96 94,96')+line('30,44 98,44')+line('38,45 25,70 51,70 38,45')+line('90,45 77,70 103,70 90,45')+ring(64, 30, 7),
        'public_financial_backstops': line('24,99 104,99')+line('30,96 30,55 64,29 98,55 98,96')+line('44,96 44,63 64,49 84,63 84,96')+line('54,96 54,73 74,73 74,96')+line('64,29 64,17'),
    }


def main():
    for name, content in glyphs().items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">'
               f'<circle cx="64" cy="64" r="56" fill="#192834" stroke="{GOLD}" stroke-width="3"/>'
               +content+'</svg>\n')
        (ROOT/f'assets_source/icons/bfl_{name}.svg').write_text(svg, encoding='utf-8')


if __name__ == '__main__':
    main()
