# coding:utf-8

from typing import (Any, Callable, Dict, List, Optional, Sequence,
                    Set, Type, Union)

from fastapi import params
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.encoders import DictIntStrAny, SetIntStr
from fastapi.routing import APIRoute, APIRouter
from fastapi.utils import (generate_unique_id,
                           get_value_or_default)
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import ASGIApp


class DeferredAPIRoute(object):
    def __init__(
            self,
            path: str,
            endpoint: Callable[..., Any],
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                JSONResponse
            ),
            name: Optional[str] = None,
            route_class_override: Optional[Type[APIRoute]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            openapi_extra: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Union[
                Callable[["APIRoute"], str], DefaultPlaceholder
            ] = Default(generate_unique_id),
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.response_model = response_model
        self.status_code = status_code
        self.tags = tags
        self.dependencies = dependencies
        self.summary = summary
        self.description = description
        self.response_description = response_description
        self.responses = responses
        self.deprecated = deprecated
        self.methods = methods
        self.operation_id = operation_id
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none
        self.include_in_schema = include_in_schema
        self.response_class = response_class
        self.name = name
        self.route_class_override = route_class_override
        self.callbacks = callbacks
        self.openapi_extra = openapi_extra
        self.generate_unique_id_function = generate_unique_id_function


class DeferredAPIWebSocketRoute(object):
    def __init__(
            self,
            path: str,
            endpoint: Callable[..., Any],
            *,
            name: Optional[str] = None,
    ) -> None:
        self.path = path
        self.endpoint = endpoint
        self.name = name


class DeferredAPIRouter(APIRouter):
    def __init__(
            self,
            *,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            routes: Optional[List[routing.BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[APIRoute] = APIRoute,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> None:
        # super().__init__(
        #     prefix=prefix,
        #     tags=tags,
        #     dependencies=dependencies,
        #     default_response_class=default_response_class,
        #     responses=responses,
        #     callbacks=callbacks,
        #     routes=routes,
        #     redirect_slashes=redirect_slashes,
        #     default=default,
        #     dependency_overrides_provider=dependency_overrides_provider,
        #     route_class=route_class,
        #     on_startup=on_startup,
        #     on_shutdown=on_shutdown,
        #     deprecated=deprecated,
        #     include_in_schema=include_in_schema
        # )
        self.default_response_class = default_response_class
        self.deprecated = deprecated
        self.include_in_schema = include_in_schema
        self.generate_unique_id_function = generate_unique_id_function

        self.deferred_routes = []

    def register(
            self,
            router: APIRouter,
            *,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> None:
        combined_routes = self.combine_routes(
            self.deferred_routes,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            router_default_response_class=router.default_response_class,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function
        )
        self.deferred_routes = combined_routes
        for route in self.deferred_routes:
            if isinstance(route, DeferredAPIRoute):
                router.add_api_route(
                    path=route.path,
                    endpoint=route.endpoint,
                    response_model=route.response_model,
                    status_code=route.status_code,
                    tags=route.tags,
                    dependencies=route.dependencies,
                    summary=route.summary,
                    description=route.description,
                    response_description=route.response_description,
                    responses=route.responses,
                    deprecated=route.deprecated or deprecated or self.deprecated,
                    methods=route.methods,
                    operation_id=route.operation_id,
                    response_model_include=route.response_model_include,
                    response_model_exclude=route.response_model_exclude,
                    response_model_by_alias=route.response_model_by_alias,
                    response_model_exclude_unset=route.response_model_exclude_unset,
                    response_model_exclude_defaults=route.response_model_exclude_defaults,
                    response_model_exclude_none=route.response_model_exclude_none,
                    include_in_schema=route.include_in_schema
                                      and self.include_in_schema
                                      and include_in_schema,
                    response_class=route.response_class,
                    name=route.name,
                    route_class_override=route.route_class_override,
                    callbacks=route.callbacks,
                    openapi_extra=route.openapi_extra
                )
            elif isinstance(route, DeferredAPIWebSocketRoute):
                router.add_api_websocket_route(
                    path=route.path,
                    endpoint=route.endpoint,
                    name=route.name
                )

    def add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                JSONResponse
            ),
            name: Optional[str] = None,
            route_class_override: Optional[Type[APIRoute]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            openapi_extra: Optional[Dict[str, Any]] = None,
            generate_unique_id_function: Union[
                Callable[[APIRoute], str], DefaultPlaceholder
            ] = Default(generate_unique_id),
    ) -> None:
        route = DeferredAPIRoute(
            path=path,
            endpoint=endpoint,
            response_model=response_model,
            status_code=status_code,
            tags=tags,
            dependencies=dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses or {},
            deprecated=deprecated,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema,
            response_class=response_class,
            name=name,
            route_class_override=route_class_override,
            callbacks=callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=generate_unique_id_function
        )
        self.deferred_routes.append(route)

    def add_api_websocket_route(
            self, path: str, endpoint: Callable[..., Any], name: Optional[str] = None
    ) -> None:
        route = DeferredAPIWebSocketRoute(
            path=path,
            endpoint=endpoint,
            name=name,
        )
        self.deferred_routes.append(route)

    def combine_routes(
            self,
            routes: List[Union["DeferredAPIRoute", "DeferredAPIWebSocketRoute"]],
            *,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            router_default_response_class: Type[Response] = Default(JSONResponse),
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> List[Union[DeferredAPIRoute, DeferredAPIWebSocketRoute]]:
        if prefix:
            assert prefix.startswith("/"), "A path prefix must start with '/'"
            assert not prefix.endswith(
                "/"
            ), "A path prefix must not end with '/', as the routes will start with '/'"
        else:
            for r in routes:
                path = getattr(r, "path")
                name = getattr(r, "name", "unknown")
                if path is not None and not path:
                    raise Exception(
                        f"Prefix and path cannot be both empty (path operation: {name})"
                    )
        if responses is None:
            responses = {}
        combined_routes = []
        for route in routes:
            if isinstance(route, DeferredAPIRoute):
                combined_responses = {**responses, **route.responses}
                use_response_class = get_value_or_default(
                    route.response_class,
                    router_default_response_class,
                    default_response_class,
                    self.default_response_class,
                )
                current_tags = []
                if tags:
                    current_tags.extend(tags)
                if route.tags:
                    current_tags.extend(route.tags)
                current_dependencies: List[params.Depends] = []
                if dependencies:
                    current_dependencies.extend(dependencies)
                if route.dependencies:
                    current_dependencies.extend(route.dependencies)
                current_callbacks = []
                if callbacks:
                    current_callbacks.extend(callbacks)
                if route.callbacks:
                    current_callbacks.extend(route.callbacks)
                current_generate_unique_id = get_value_or_default(
                    route.generate_unique_id_function,
                    generate_unique_id_function,
                    self.generate_unique_id_function,
                )
                combined_routes.append(DeferredAPIRoute(
                    prefix + route.path,
                    route.endpoint,
                    response_model=route.response_model,
                    status_code=route.status_code,
                    tags=current_tags,
                    dependencies=current_dependencies,
                    summary=route.summary,
                    description=route.description,
                    response_description=route.response_description,
                    responses=combined_responses,
                    deprecated=route.deprecated or deprecated or self.deprecated,
                    methods=route.methods,
                    operation_id=route.operation_id,
                    response_model_include=route.response_model_include,
                    response_model_exclude=route.response_model_exclude,
                    response_model_by_alias=route.response_model_by_alias,
                    response_model_exclude_unset=route.response_model_exclude_unset,
                    response_model_exclude_defaults=route.response_model_exclude_defaults,
                    response_model_exclude_none=route.response_model_exclude_none,
                    include_in_schema=route.include_in_schema
                                      and self.include_in_schema
                                      and include_in_schema,
                    response_class=use_response_class,
                    name=route.name,
                    route_class_override=route.route_class_override,
                    callbacks=current_callbacks,
                    openapi_extra=route.openapi_extra,
                    generate_unique_id_function=current_generate_unique_id
                ))
            elif isinstance(route, DeferredAPIWebSocketRoute):
                combined_routes.append(DeferredAPIWebSocketRoute(
                    prefix + route.path, route.endpoint, name=route.name
                ))
        return combined_routes

    def include_router(
            self,
            router: "DeferredAPIRouter",
            *,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[params.Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            generate_unique_id_function: Callable[[APIRoute], str] = Default(
                generate_unique_id
            ),
    ) -> None:
        combined_routes = self.combine_routes(
            router.deferred_routes,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            router_default_response_class=router.default_response_class,
            default_response_class=default_response_class,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            generate_unique_id_function=generate_unique_id_function
        )
        self.deferred_routes.extend(combined_routes)
        # for handler in router.on_startup:
        #     self.add_event_handler("startup", handler)
        # for handler in router.on_shutdown:
        #     self.add_event_handler("shutdown", handler)
