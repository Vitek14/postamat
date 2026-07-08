import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import PostamatService
from .models import Postamat
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError


def admin_login_redirect(request):
    return redirect('/accounts/login/?next=/admin/')


def user_in_groups(user, group_names):
    from django.contrib.auth.models import Group
    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        if user.groups.filter(name=name).exists():
            return True
    return False


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def place_order(request, postamat_id) -> HttpResponseForbidden | JsonResponse:
    """Endpoint to create an order for courier.

    :param request: Http request object. Expects json like: {"order_id": "123", "user_phone": "+79991234567"}
    :param postamat_id: string with postamat id
    :return: JsonResponse with 200 status
    :rtype: JsonResponse
    :raises Http404: If postamat id is not valid or can't be found.
    :raises Http400: If unknown error occurs.
    :raises HttpResponseForbidden: If user does not have permission to place order.
    """
    if not user_in_groups(request.user, ['Couriers', 'Admins']):
        return HttpResponseForbidden("Only couriers and administrators can place orders")

    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        user_phone = data.get('user_phone')
        if not order_id or not user_phone:
            return JsonResponse({'error': 'Missing order_id or user_phone'}, status=400)

        service = PostamatService(postamat_id)
        result = service.place_order(order_id, user_phone)
        return JsonResponse(result, status=200)

    except Postamat.DoesNotExist:
        return JsonResponse({'error': 'Postamat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def get_order(request, postamat_id) -> HttpResponseForbidden | JsonResponse:
    """Endpoint to get an order from courier.

    :param request: Http request object. Expects json like: {"receive_code": "123456"}
    :param postamat_id: string with postamat id
    :return: JsonResponse with 200 status
    :rtype: JsonResponse
    :raises Http404: If postamat id is not valid or can't be found.
    :raises Http400: If unknown error occurs.
    :raises HttpResponseForbidden: If user does not have permission to get order.
    """
    if not user_in_groups(request.user, ['Users', 'Admins']):
        return HttpResponseForbidden("Only users and administrators can get orders")

    try:
        data = json.loads(request.body)
        receive_code = data.get('receive_code')
        if not receive_code:
            return JsonResponse({'error': 'Missing receive_code'}, status=400)

        service = PostamatService(postamat_id)
        result = service.get_order(receive_code)
        return JsonResponse(result, status=200)

    except Postamat.DoesNotExist:
        return JsonResponse({'error': 'Postamat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def index(request):
    return render(request, 'postamat/index.html')


@login_required
def place_order_ui(request, postamat_id):
    if not user_in_groups(request.user, ['Couriers', 'Admins']):
        return HttpResponseForbidden("You don't have enough rights to place orders")

    context = {'postamat_id': postamat_id}
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        user_phone = request.POST.get('user_phone')
        if not order_id or not user_phone:
            context['result'] = {'error': 'All fields needs to be filled'}
        else:
            try:
                service = PostamatService(postamat_id)
                result = service.place_order(order_id, user_phone)
                context['result'] = {
                    'success': f"Order {result['order_id']} placed in cell {result['cell_number']}. Code for user: {result['receive_code']}"
                }
            except ValidationError as e:
                context['result'] = {'error': str(e)}
            except Exception as e:
                context['result'] = {'error': f'Error: {e}'}
    return render(request, 'postamat/place_order.html', context)


@login_required
def get_order_ui(request, postamat_id):
    if not user_in_groups(request.user, ['Users', 'Admins']):
        return HttpResponseForbidden("You don't have enough rights to get orders")

    context = {'postamat_id': postamat_id}
    if request.method == 'POST':
        receive_code = request.POST.get('receive_code')
        if not receive_code:
            context['result'] = {'error': 'Enter a code'}
        else:
            try:
                service = PostamatService(postamat_id)
                result = service.get_order(receive_code)
                context['result'] = {
                    'success': f"Your order {result['order_id']} is in a cell {result['cell_number']} is gived to you."
                }
            except ValidationError as e:
                context['result'] = {'error': str(e)}
            except Exception as e:
                context['result'] = {'error': f'Error: {e}'}
    return render(request, 'postamat/get_order.html', context)
