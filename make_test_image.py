import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(5, 6))
ax.axis('off')

text = """
INVOICE

Vendor: ABC Traders
Invoice #: INV-2026-001

Item            Qty   Price   Subtotal
Widget A         2    100.00   200.00
Widget B         1    250.00   250.00

Subtotal:                    450.00
Tax (10%):                     45.00
Grand Total:                 495.00
"""

ax.text(0.05, 0.95, text, fontsize=11, family='monospace',
        verticalalignment='top', transform=ax.transAxes)

plt.savefig('test_invoice.png', dpi=100, bbox_inches='tight')
print("Saved test_invoice.png")