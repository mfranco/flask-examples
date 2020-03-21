from authlib.integrations.flask_oauth2 import AuthorizationServer, ResourceProtector
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.oauth2.rfc6749 import grants
from werkzeug.security import gen_salt


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def create_authorization_code(sef, client, grant_user, request):
        code = gen_salt(48)
        item = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.id,
        )
        session.add(item)
        session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        session.delete(authorization_code)
        session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
        if token and token.is_refresh_token_active():
            return token

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)

    def revoke_old_credential(self, credential):
        credential.revoked = True
        session.add(credential)
        session.commit()






def config_oauth(app, db):

    with app.app_context():
        pool = create_pool()

        save_token = create_save_token_func(pool.get_session(), OAuth2Token)

        authorization = AuthorizationServer(
            query_client=query_client,
            save_token=save_token,
        )

        authorization.init_app(app)

        ## support all grants
        authorization.register_grant(AuthorizationCodeGrant)
        authorization.register_grant(PasswordGrant)
        authorization.register_grant(RefreshTokenGrant)
        ## support revocation
        revocation_cls = create_revocation_endpoint(pool.get_session(), OAuth2Token)
        authorization.register_endpoint(revocation_cls)

        ## protect resource
        require_oauth = ResourceProtector()
        bearer_cls = create_bearer_token_validator(pool.get_session(), OAuth2Token)
        require_oauth.register_token_validator(bearer_cls())
