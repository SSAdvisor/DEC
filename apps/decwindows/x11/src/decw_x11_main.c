#include "decw_x11.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static void print_usage(const char* prog) {
    printf("Usage: %s [options]\n", prog);
    printf("DECwindows X11/Motif 1.1 Interfacing Engine (%s)\n\n", decw_x11_version());
    printf("Options:\n");
    printf("  --probe                  Probe X11 server connection and display geometry\n");
    printf("  --check-gui              Check if interactive TTY + reachable X11 DISPLAY exist\n");
    printf("  --version                Print library version\n");
    printf("  --app <id>               Application identifier (decterm, clock, notepad, etc.)\n");
    printf("  --title <title>          Window title string\n");
    printf("  --frame <path>           Path to rendered frame buffer text file\n");
    printf("  --state <path>           Path to persistent BASIC-PLUS-2 state file (.dat)\n");
    printf("  --exec <binary>          Backing BASIC-PLUS-2 executable for interactive callbacks\n");
    printf("  --export-verb <verb>     Frame export verb (default: EXPORT)\n");
    printf("  --display <dpy>          Target X11 display string (default: $DISPLAY)\n");
    printf("  --geometry <WxH>         Window dimensions in pixels (default: 780x600)\n");
    printf("  --autoclose <ms>         Auto-close window after <ms> milliseconds following Expose\n");
    printf("  --verify                 Verify X11 window creation, Expose rendering, and exit\n");
    printf("  --test-interact          Synthesize X11 Motif button click event after Expose\n");
}

int main(int argc, char** argv) {
    DecwWindowConfig cfg;
    memset(&cfg, 0, sizeof(cfg));
    strcpy(cfg.app_id, "decwindows");
    strcpy(cfg.title, "DECwindows Motif 1.1 Workstation Window");
    strcpy(cfg.export_verb, "EXPORT");
    cfg.width = 780;
    cfg.height = 600;

    int do_probe = 0;
    int do_check_gui = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "--version") == 0) {
            printf("%s\n", decw_x11_version());
            return 0;
        } else if (strcmp(argv[i], "--probe") == 0) {
            do_probe = 1;
        } else if (strcmp(argv[i], "--check-gui") == 0) {
            do_check_gui = 1;
        } else if (strcmp(argv[i], "--verify") == 0) {
            cfg.verify_only = 1;
        } else if (strcmp(argv[i], "--test-interact") == 0) {
            cfg.test_interact = 1;
        } else if (strcmp(argv[i], "--app") == 0 && i + 1 < argc) {
            strncpy(cfg.app_id, argv[++i], sizeof(cfg.app_id) - 1);
        } else if (strcmp(argv[i], "--title") == 0 && i + 1 < argc) {
            strncpy(cfg.title, argv[++i], sizeof(cfg.title) - 1);
        } else if (strcmp(argv[i], "--frame") == 0 && i + 1 < argc) {
            strncpy(cfg.frame_path, argv[++i], sizeof(cfg.frame_path) - 1);
        } else if (strcmp(argv[i], "--state") == 0 && i + 1 < argc) {
            strncpy(cfg.state_path, argv[++i], sizeof(cfg.state_path) - 1);
        } else if (strcmp(argv[i], "--exec") == 0 && i + 1 < argc) {
            strncpy(cfg.exec_bin, argv[++i], sizeof(cfg.exec_bin) - 1);
        } else if (strcmp(argv[i], "--export-verb") == 0 && i + 1 < argc) {
            strncpy(cfg.export_verb, argv[++i], sizeof(cfg.export_verb) - 1);
        } else if (strcmp(argv[i], "--display") == 0 && i + 1 < argc) {
            strncpy(cfg.display_name, argv[++i], sizeof(cfg.display_name) - 1);
        } else if (strcmp(argv[i], "--geometry") == 0 && i + 1 < argc) {
            int w = 0, h = 0;
            if (sscanf(argv[++i], "%dx%d", &w, &h) == 2 && w >= 320 && h >= 240) {
                cfg.width = w;
                cfg.height = h;
            }
        } else if (strcmp(argv[i], "--autoclose") == 0 && i + 1 < argc) {
            cfg.autoclose_ms = atoi(argv[++i]);
        }
    }

    if (do_check_gui) {
        const char* force_cli = getenv("DECW_FORCE_CLI");
        if (force_cli && force_cli[0] && strcmp(force_cli, "0") != 0) {
            return 1;
        }
        const char* force_x11 = getenv("DECW_FORCE_X11");
        if (!force_x11 || !force_x11[0] || strcmp(force_x11, "0") == 0) {
            if (!isatty(STDIN_FILENO)) {
                return 1;
            }
        }
        char info[256];
        return (decw_x11_probe_display(cfg.display_name, info, sizeof(info)) == 0) ? 0 : 1;
    }

    if (do_probe) {
        char info[256];
        int rc = decw_x11_probe_display(cfg.display_name, info, sizeof(info));
        printf("%s\n", info);
        return (rc == 0) ? 0 : 1;
    }

    decw_x11_resolve_defaults(&cfg, argv[0]);
    return decw_x11_run_window(&cfg);
}
