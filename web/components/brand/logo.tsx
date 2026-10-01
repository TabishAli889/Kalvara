/**
 * Kalvara brand mark: a geometric "K" whose arm and leg are a detached
 * chevron, so it also reads as a forward caret. Monochrome on purpose — the
 * glyph inherits currentColor, so it inverts with the theme like the rest of
 * the neutral palette.
 */
import { cn } from "@/lib/utils";

export function KalvaraMark({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      className={cn("size-full", className)}
    >
      <g
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M6.4 4V20" />
        <path d="M17.7 4L9.7 12L17.7 20" />
      </g>
    </svg>
  );
}

/** The mark in its badge — a filled squircle that flips with the theme. */
export function KalvaraLogo({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "grid size-7 shrink-0 place-items-center rounded-lg bg-foreground text-background",
        className,
      )}
    >
      <KalvaraMark className="size-[18px]" />
    </span>
  );
}
