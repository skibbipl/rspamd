SET(RSPAMADMSRC rspamadm.c commands.c pw.c keypair.c configtest.c
        ${CMAKE_BINARY_DIR}/src/workers.c
        ${CMAKE_BINARY_DIR}/src/modules.c
        ${CMAKE_SOURCE_DIR}/src/controller.c
        ${CMAKE_SOURCE_DIR}/src/fuzzy_storage.c
        ${CMAKE_SOURCE_DIR}/src/lua_worker.c
        ${CMAKE_SOURCE_DIR}/src/smtp_proxy.c
        ${CMAKE_SOURCE_DIR}/src/worker.c
        ${CMAKE_SOURCE_DIR}/src/http_proxy.c fuzzy_merge.c configdump.c)

ADD_EXECUTABLE(rspamadm ${RSPAMADMSRC})
TARGET_LINK_LIBRARIES(rspamadm rspamd-server)
TARGET_LINK_LIBRARIES(rspamadm ${RSPAMD_REQUIRED_LIBRARIES})
TARGET_LINK_LIBRARIES(rspamadm stemmer)
TARGET_LINK_LIBRARIES(rspamadm rspamd-actrie)

IF (NOT DEBIAN_BUILD)
    SET_TARGET_PROPERTIES(rspamadm PROPERTIES VERSION ${RSPAMD_VERSION})
ENDIF (NOT DEBIAN_BUILD)

INSTALL(TARGETS rspamadm RUNTIME DESTINATION bin)