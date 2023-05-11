#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from neutron_lib import policy as neutron_policy
from oslo_policy import policy


# For completion of the phase 1
# https://governance.openstack.org/tc/goals/selected/consistent-and-secure-rbac.html#phase-1
# there is now ADMIN role
ADMIN = "rule:admin_only"

# This check string is the primary use case for typical end-users, who are
# working with resources that belong to a project (e.g., creating ports and
# routers).
PROJECT_MEMBER = 'role:member and project_id:%(project_id)s'

# This check string should only be used to protect read-only project-specific
# resources. It should not be used to protect APIs that make writable changes
# (e.g., updating a router or deleting a port).
PROJECT_READER = 'role:reader and project_id:%(project_id)s'

# The following are common composite check strings that are useful for
# protecting APIs designed to operate with multiple scopes (e.g.,
# an administrator should be able to delete any router in the deployment, a
# project member should only be able to delete routers in their project).
ADMIN_OR_PROJECT_MEMBER = (
    '(' + ADMIN + ') or (' + PROJECT_MEMBER + ')')
ADMIN_OR_PROJECT_READER = (
    '(' + ADMIN + ') or (' + PROJECT_READER + ')')

# Additional rules needed in Neutron
RULE_NET_OWNER = 'rule:network_owner'
RULE_PARENT_OWNER = 'rule:ext_parent_owner'
RULE_SG_OWNER = 'rule:sg_owner'

# In some cases we need to check owner of the parent resource, it's like that
# for example for QoS rules (check owner of QoS policy rule belongs to) or
# Floating IP port forwarding (check owner of FIP which PF is using). It's like
# that becasue those resources (QOS rules, FIP PFs) don't have project_id
# attribute at all and they belongs to the same project as parent resource (QoS
# policy, FIP).
PARENT_OWNER_MEMBER = 'role:member and ' + RULE_PARENT_OWNER
PARENT_OWNER_READER = 'role:reader and ' + RULE_PARENT_OWNER
ADMIN_OR_PARENT_OWNER_MEMBER = (
    '(' + ADMIN + ') or (' + PARENT_OWNER_MEMBER + ')')
ADMIN_OR_PARENT_OWNER_READER = (
    '(' + ADMIN + ') or (' + PARENT_OWNER_READER + ')')


rules = [
    policy.RuleDefault(
        'context_is_admin',
        'role:admin',
        description='Rule for cloud admin access'),
    policy.RuleDefault(
        'owner',
        'tenant_id:%(tenant_id)s',
        description='Rule for resource owner access'),
    policy.RuleDefault(
        'admin_or_owner',
        neutron_policy.policy_or('rule:context_is_admin',
                                 'rule:owner'),
        description='Rule for admin or owner access'),
    policy.RuleDefault(
        'context_is_advsvc',
        'role:advsvc',
        description='Rule for advsvc role access'),
    policy.RuleDefault(
        'admin_or_network_owner',
        neutron_policy.policy_or('rule:context_is_admin',
                                 'tenant_id:%(network:tenant_id)s'),
        description='Rule for admin or network owner access'),
    policy.RuleDefault(
        'admin_owner_or_network_owner',
        neutron_policy.policy_or('rule:owner',
                                 neutron_policy.RULE_ADMIN_OR_NET_OWNER),
        description=('Rule for resource owner, '
                     'admin or network owner access')),
    policy.RuleDefault(
        'network_owner',
        'tenant_id:%(network:tenant_id)s',
        description='Rule for network owner access'),
    policy.RuleDefault(
        'admin_only',
        'rule:context_is_admin',
        description='Rule for admin-only access'),
    policy.RuleDefault(
        'regular_user',
        '',
        description='Rule for regular user access'),
    # TODO(amotoki): Should be renamed to shared_network? It seems clearer.
    policy.RuleDefault(
        'shared',
        'field:networks:shared=True',
        description='Rule of shared network'),
    policy.RuleDefault(
        'default',
        neutron_policy.RULE_ADMIN_OR_OWNER,
        description='Default access rule'),
    policy.RuleDefault(
        'admin_or_ext_parent_owner',
        neutron_policy.policy_or('rule:context_is_admin',
                                 'tenant_id:%(ext_parent:tenant_id)s'),
        description='Rule for common parent owner check'),
    policy.RuleDefault(
        'ext_parent_owner',
        'tenant_id:%(ext_parent:tenant_id)s',
        description='Rule for common parent owner check'),
    policy.RuleDefault(
        name='sg_owner',
        check_str='tenant_id:%(security_group:tenant_id)s',
        description='Rule for security group owner access'),
]


def list_rules():
    return rules
