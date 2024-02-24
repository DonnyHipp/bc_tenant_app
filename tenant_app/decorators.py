from django.contrib import messages

from django.shortcuts import redirect


def ajax_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.META.get("HTTP_HX_REQUEST"):
            return view_func(request, *args, **kwargs)
        else:
            return redirect("/")

    return _wrapped_view
