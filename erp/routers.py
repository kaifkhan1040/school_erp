from rest_framework_nested import routers
from users.viewset import userSignupView,DesignationViewSet
from task.viewset import TaskViewSet, CommentViewSet, AttachmentViewSet
# from base.api.routers import PlutonicRouter
from rest_framework.routers import DefaultRouter, SimpleRouter

restricted_router = DefaultRouter()
### Sharewithevendviewset
restricted_router.register('user',userSignupView,basename='user')
restricted_router.register('designation',DesignationViewSet,basename='designation')
restricted_router.register('task',TaskViewSet,basename='task')
restricted_router.register('comments',CommentViewSet,basename='comments')
restricted_router.register('attachments',AttachmentViewSet,basename='attachments')
