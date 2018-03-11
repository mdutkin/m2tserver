__author__ = 'Maxim Dutkin (max@dutkin.ru)'


class AuthorizationMixin:
    def check_authorization(self):
        print('check_authorization from AuthorizationMixin')
        return True