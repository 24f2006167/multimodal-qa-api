import matplotlib.pyplot as plt

labels = ['Housing', 'Food', 'Transport', 'Savings']
sizes = [40, 25, 15, 20]

fig, ax = plt.subplots(figsize=(5, 5))
ax.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90)
ax.set_title("Monthly Budget Breakdown")

plt.savefig('test_piechart.png', dpi=100, bbox_inches='tight')
print("Saved test_piechart.png")