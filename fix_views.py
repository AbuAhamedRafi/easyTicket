#!/usr/bin/env python
"""Fix views to use uid instead of id"""

# Read Orders/views.py
with open("Orders/views.py", "r") as f:
    content = f.read()

# Replace order.id with order.uid
content = content.replace("order.id", "order.uid")
# Replace order.event.id with order.event.uid
content = content.replace("order.event.uid", "order.event.uid")  # Already done above
# Replace order.user.id with order.user.uid
content = content.replace("order.user.uid", "order.user.uid")  # Already done above

# Write back
with open("Orders/views.py", "w") as f:
    f.write(content)

print("Updated Orders/views.py")
