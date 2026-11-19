from django.http import Http404


class OwnerQuerysetMixin:
    owner_permission = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        if user.has_perm(self.owner_permission):
            own = qs.filter(owner=user)
            others = qs.exclude(owner__is_superuser=True).exclude(owner__groups__name='managers')
            return own | others
        return qs.filter(owner=user)


class ManagerRequiredMixin:
    manager_permission = None

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.has_perm(self.manager_permission)):
            raise Http404
        return super().dispatch(request, *args, **kwargs)