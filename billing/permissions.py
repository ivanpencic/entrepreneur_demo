def deny_all(request):
	return False


def allow_any(request):
	return True


def filter_grid_actions(request, actions):
	filtered = []
	for action, permission in actions:
		if permission(request):
			filtered.append(action)
	return filtered
