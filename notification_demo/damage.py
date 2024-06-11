"""
Normally when we do attacks the attacking object needs to retrieve every possible thing it could damage, and then
do a collision check which means retrieving all damageable objects.

Instead, if they make an attack object and then push a "do_attack" notification another system can pick up their
attack object and the attacker doesn't need to worry about who they will hit.

This also goes for health-pools when a damageable object takes damage it can send out notifications that it took damage,
or if you wanted to do resistances if it didn't take damage, then you can send a notification when the object dies.
"""