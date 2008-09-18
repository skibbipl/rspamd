#ifndef RSPAMD_MEM_POOL_H
#define RSPAMD_MEM_POOL_H

#include <sys/types.h>
#include <glib.h>

typedef struct memory_pool_s {
	u_char *begin;
	u_char *pos;
	size_t len;
	struct memory_pool_s *next;
} memory_pool_t;

memory_pool_t* memory_pool_new (size_t size);
void* memory_pool_alloc (memory_pool_t* pool, size_t size);
void memory_pool_delete (memory_pool_t* pool);

#define memory_pool_free(x) ((x)->pos - (x)->begin)

#endif
