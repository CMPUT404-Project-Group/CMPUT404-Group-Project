from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


@login_required
def index(request):
    return render(request, 'app/index.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('app:index')
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})
