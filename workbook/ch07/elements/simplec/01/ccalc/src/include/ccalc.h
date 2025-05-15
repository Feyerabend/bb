// include/ccalc.h
#ifndef CCALC_H
#define CCALC_H

// core
#include "../src/core/arithmetic.h"
#include "../src/core/advanced.h"
#include "../src/core/fixedpoint.h"

// utilities (if needed by API users)
#include "../src/utils/logger.h"
#include "../src/utils/validators.h"

// library version information
#define CCALC_VERSION_MAJOR 1
#define CCALC_VERSION_MINOR 0
#define CCALC_VERSION_PATCH 0

// library initialization (if needed)
int ccalc_init(void);
void ccalc_cleanup(void);

#endif // CCALC_H