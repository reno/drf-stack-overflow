
def is_owner(obj, user):
    """Checks if model instance belongs to a user."""
    if obj.user.id == user.id:
        return True
    return False


def update_votes(obj, user, value):
    """Updates votes for a question or answer."""
    obj.votes.update_or_create(
        user=user, defaults={"value": value},
    )
    obj.count_votes()