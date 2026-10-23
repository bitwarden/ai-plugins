export type BeadStatus = "in_progress" | "blocked" | "open";

export type Bead = {
  id: string;
  title: string;
  status: BeadStatus;
  priority: number;
  type: string;
};

export type BeadsSnapshot = { beads: Bead[]; error?: string };

declare module "claude-code" {
  interface PluginState {
    "bitwarden-beads-tools": { snapshot: BeadsSnapshot | null };
  }
}
