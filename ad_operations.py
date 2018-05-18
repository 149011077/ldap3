from ldap3 import Server, Connection, BASE, LEVEL, SUBTREE, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, MODIFY_REPLACE
import json

OBJECT_CLASS = ['top', 'person', 'organizationalPerson', 'user']
LDAP_BASE_DN = 'dc=aukeyis,dc=com'
search_filter = "(displayName={0}*)"

def conn_ad():
    server = Server('ldaps://10.1.1.2', use_ssl=True)
    conn = Connection(server, user="aukeyis\\zhangzp", password="zhangzp@888", auto_bind=True)
    return conn


def get_attributes(username, forename, surname):
    return {
        "displayName": username,
        "sAMAccountName": username,
        "userPrincipalName": "{0}@aukeyis.com".format(username),
        "name": username,
        "givenName": forename,
        "sn": surname
    }


def get_dn(username):
    return "CN={0},OU=it,OU=test,DC=aukeyis,DC=com".format(username)


def get_groups(cn, ou):
    return '{0},{1},DC=aukeyis,DC=com'.format(cn, ou)

def get_user_dn(username):
    conn = conn_ad()
    # conn.search(search_base=LDAP_BASE_DN, search_filter=search_filter.format(username), search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    conn.search(search_base=LDAP_BASE_DN, search_filter="(objectclass=organizationalUnit)", search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    result = json.loads(conn.response_to_json())
    res = result["entries"][0]['dn']
    print(result)
    conn.unbind()
    return res

def get_group_dn(groupname):
    conn = conn_ad()
    conn.search(search_base=LDAP_BASE_DN, search_filter="(cn=%s)" %groupname, search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)  #objectclass=group
    result = json.loads(conn.response_to_json())
    res = result["entries"][0]['dn']
    # for entry in conn.response:
    #     result = entry['dn']
    conn.unbind()
    return res


def find_ad_users(username):
    conn = conn_ad()
    conn.search(search_base=LDAP_BASE_DN, search_filter=search_filter.format(username), search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    return json.loads(conn.response_to_json())


def find_ad_group(groupname):
    conn = conn_ad()
    conn.search(search_base=LDAP_BASE_DN, search_filter="(objectclass=group,cn='itzu')", search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    return json.loads(conn.response_to_json())


def create_ad_user(username, forename, surname, new_password):
    conn = conn_ad()
    attributes = get_attributes(username, forename, surname)
    user_dn = get_dn(username)
    result = conn.add(dn=user_dn, object_class=OBJECT_CLASS, attributes=attributes)
    if not result:
        msg = "ERROR: User '{0}' was not created:{1}".format(username, conn.result.get("description"))
        raise Exception(msg)
    conn.extend.microsoft.unlock_account(user=user_dn)
    conn.extend.microsoft.modify_password(user=user_dn, new_password=new_password, old_password=None)
    enable_account = {"userAccountControl": (MODIFY_REPLACE, [512])}
    conn.modify(user_dn,changes=enable_account)
    conn.extend.microsoft.add_members_to_groups(user_dn, get_groups('CN=itzu','OU=test'))   #'CN=itzu,OU=test,DC=aukeyis,DC=com'
    conn.unbind()


def user_remove_group():
    conn = conn_ad()
    result = conn.extend.microsoft.remove_members_from_groups(get_dn('user8'), get_groups('CN=itzu','OU=test'))
    print(result)


def add_ou():
    conn = conn_ad()
    conn.add('ou=its,ou=test,dc=aukeyis,dc=com','organizationalUnit')
    res = conn.result
    print(res)
    conn.unbind()

def add_group():
    conn = conn_ad()
    conn.add('cn=cctv,ou=it,ou=test,dc=aukeyis,dc=com','group')
    res = conn.result
    print(res)
    conn.unbind()


def get_all_ou(dn):
    conn = conn_ad()
    # conn.search(search_base=LDAP_BASE_DN, search_filter=search_filter.format(username), search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    conn.search(search_base=dn, search_filter="(objectclass=organizationalUnit)", search_scope=LEVEL, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    for entry in conn.response:
        result = ''
        if entry.__contains__('dn'):
            result = entry['dn']
            print(result)
            get_all_user(result)
        if result:
            get_all_ou(result)
    conn.unbind()


def get_all_user(dn):
    conn = conn_ad()
    conn.search(search_base=dn, search_filter="(objectclass=user)", search_scope=LEVEL,
                attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
    for entry in conn.response:
        if entry.__contains__('dn'):    #displayName
            result = entry['dn']
            print(result)
    conn.unbind()

def move_user():
    conn = conn_ad()
    res = conn.modify_dn('cn=user5,ou=it,ou=test,dc=aukeyis,dc=com', 'cn=user5', new_superior='ou=sys002,ou=its,ou=test,dc=aukeyis,dc=com')
    print(conn.result)
    conn.unbind()

def modi():
    conn = conn_ad()
    conn.modify('cn=zmqq,ou=it,ou=test', {'givenName': [(MODIFY_REPLACE, ['givenname-zmqq'])]})
    print(conn.result)
    conn.unbind()

def del_obj():
    conn = conn_ad()
    conn = Connection(s,user='zhangzp',password='zhangzp@888')
    conn.delete('cn=zmqq,ou=it,ou=test,dc=aukeyis,dc=com')
    print(conn.result)
    conn.unbind()



if __name__ == "__main__":
    # print(find_ad_users('itzu'))
    # print(find_ad_group('itzu'))
    # create_ad_user('user8', 'user8', 'user8','user8@888')
    # user_remove_group()
    # print(get_group_dn('administrators'))
    # print(get_user_dn('test'))
    # add_ou()
    # add_group()
    # get_all_ou('ou=test,dc=aukeyis,dc=com')
    get_all_user('ou=test,dc=aukeyis,dc=com')
