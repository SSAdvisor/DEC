/* ========================================================================== *
 * DEC VAX C V3.2 Demonstration Program (DEMO.C)                              *
 * Digital Equipment Corporation VAX/VMS V5.5-2                               *
 * ========================================================================== */
#pragma module VAXCDEMO "V03-02"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <descrip.h>

#define NUM_NODES 5
#define BONUS_POOL 4500

struct vax_node {
    int node_id;
    char *hostname;
    int mips_rating;
};

int compute_cluster_score(int total_mips, int factor) {
    return (total_mips * factor) + BONUS_POOL;
}

int main(int argc, char *argv[]) {
    $DESCRIPTOR(hdr_dsc, "========================================================");
    $DESCRIPTOR(title_dsc, "  DEC VAX C V3.2-044 ON VAX/VMS V5.5-2 (LAVC CLUSTER)  ");

    struct vax_node primary = { 101, "VAX780::SYSMGR", 1200 };
    struct vax_node *ptr = &primary;
    int loads[5] = { 150, 300, 450, 600, 750 };
    int i;
    int sum_loads = 0;
    int score;
    char *tier;

    LIB$PUT_OUTPUT(&hdr_dsc);
    LIB$PUT_OUTPUT(&title_dsc);
    LIB$PUT_OUTPUT(&hdr_dsc);

    for (i = 0; i < NUM_NODES; i++) {
        sum_loads += loads[i];
    }

    ptr->mips_rating += 300;
    score = compute_cluster_score(sum_loads, 4);

    switch (ptr->node_id) {
        case 100:
            tier = "STANDBY NODE";
            break;
        case 101:
            tier = "PRIMARY VAXCLUSTER MASTER";
            break;
        default:
            tier = "SATELLITE WORKSTATION";
            break;
    }

    printf("  CLUSTER NODE      : %s (ID=%d)\n", ptr->hostname, ptr->node_id);
    printf("  NODE ROLE         : %s\n", tier);
    printf("  UPGRADED MIPS     : %d\n", primary.mips_rating);
    printf("  WORKLOAD SUM(0..4): %d\n", sum_loads);
    printf("  VAXCLUSTER SCORE  : %d\n", score);

    LIB$PUT_OUTPUT(&hdr_dsc);
    return SS$_NORMAL;
}
