"""Authentication routes – login, logout, user management."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import shared
from app.auth import (
    clear_session_cookie,
    create_token,
    get_current_user,
    hash_password,
    set_session_cookie,
    verify_password,
)

router = APIRouter()


@router.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url='/admin', status_code=302)
    error = request.query_params.get('error', '')
    return shared.templates.TemplateResponse(request, 'login.html', {
        'request': request,
        'page': 'login',
        'error': error,
    })


@router.post('/login')
def login_submit(username: str = Form(''), password: str = Form('')):
    username = username.strip().lower()
    user = shared.db.get_user_by_username(username)
    if not user or not verify_password(password, user['password_hash']):
        return RedirectResponse(url='/login?error=invalid', status_code=303)

    token = create_token(user['user_id'], user['username'], user['role'])
    shared.db.update_user(user['user_id'], last_login=datetime.now(timezone.utc).isoformat())
    response = RedirectResponse(url='/admin', status_code=303)
    set_session_cookie(response, token)
    return response


@router.get('/logout')
def logout():
    response = RedirectResponse(url='/login', status_code=302)
    clear_session_cookie(response)
    return response


@router.get('/admin/profile', response_class=HTMLResponse)
def profile_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url='/login', status_code=302)
    return shared.templates.TemplateResponse(request, 'profile.html', {
        'request': request,
        'page': 'profile',
        'profile_user': user,
    })


@router.post('/admin/profile')
def profile_save(
    request: Request,
    display_name: str = Form(''),
    current_password: str = Form(''),
    new_password: str = Form(''),
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url='/login', status_code=302)

    updates: dict = {}
    if display_name.strip():
        updates['display_name'] = display_name.strip()

    if new_password.strip():
        if not current_password or not verify_password(current_password, user['password_hash']):
            return RedirectResponse(url='/admin/profile?error=password', status_code=303)
        from app.auth import hash_password
        try:
            updates['password_hash'] = hash_password(new_password.strip())
        except RuntimeError:
            return RedirectResponse(url='/admin/profile?error=bcrypt', status_code=303)

    if updates:
        shared.db.update_user(user['user_id'], **updates)
    return RedirectResponse(url='/admin/profile?saved=1', status_code=303)
