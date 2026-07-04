import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(4, 6))
ax.axis('off')

text = """
   FRESH MART GROCERY
   ------------------

   Milk 1L          x2    80.00
   Bread            x1    45.00
   Eggs (12)        x1    90.00
   Rice 5kg         x1   250.00

   ------------------
   TOTAL:                465.00
   ------------------
   Thank you!
"""

ax.text(0.05, 0.95, text, fontsize=11, family='monospace',
        verticalalignment='top', transform=ax.transAxes)

plt.savefig('test_receipt.png', dpi=100, bbox_inches='tight')
print("Saved test_receipt.png")