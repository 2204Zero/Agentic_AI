"use client";

import React, { useEffect, useRef, useState } from "react";

type Hex = {
  id: number;
  top: number;
  left: number;
  size: number;
  opacity: number;
  driftX: number;
  driftY: number;
  duration: number;
};

const SIZES = [60, 90, 130];
const MIN_PAD = 5;
const MAX_PAD = 95;
const MIN_DISTANCE = 12;

function randBetween(min: number, max: number) {
  return Math.random() * (max - min) + min;
}

function randInt(min: number, max: number) {
  return Math.floor(randBetween(min, max + 1));
}

function pickSize() {
  return SIZES[Math.floor(Math.random() * SIZES.length)];
}

function distance(a: { top: number; left: number }, b: { top: number; left: number }) {
  const dx = a.left - b.left;
  const dy = a.top - b.top;
  return Math.sqrt(dx * dx + dy * dy);
}

function avoidCenter(p: { top: number; left: number }) {
  return !(p.top > 40 && p.top < 60 && p.left > 40 && p.left < 60);
}

function generateEdgeBiasedPositions(total: number) {
  const points: Array<{ top: number; left: number }> = [];
  const seeds = [
    { top: randBetween(5, 15), left: randBetween(20, 80) },  // near top
    { top: randBetween(85, 95), left: randBetween(20, 80) }, // near bottom
    { top: randBetween(20, 80), left: randBetween(5, 15) },  // near left
    { top: randBetween(20, 80), left: randBetween(85, 95) }, // near right
  ];
  seeds.forEach((s) => points.push(s));

  for (let i = points.length; i < total; i++) {
    let tries = 0;
    let p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
    while (
      tries < 40 &&
      (!avoidCenter(p) || points.some((q) => distance(p, q) < MIN_DISTANCE))
    ) {
      p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
      tries++;
    }
    points.push(p);
  }
  return points;
}

function randomPositionAvoidCenter() {
  let p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
  let tries = 0;
  while (tries < 30 && !avoidCenter(p)) {
    p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
    tries++;
  }
  return p;
}

export default function HexGrid({ offsetX = 0, offsetY = 0 }: { offsetX?: number; offsetY?: number }) {
  const [hexes, setHexes] = useState<Hex[]>([]);
  const timersRef = useRef<Map<number, number>>(new Map());
  const cycleRef = useRef<(idx: number) => void>(() => {});

  useEffect(() => {
    // Initialize on client after mount to avoid SSR hydration mismatches
    const count = randInt(6, 9);
    const pos = generateEdgeBiasedPositions(count);
    setHexes(
      Array.from({ length: count }).map((_, i) => ({
        id: i,
        top: pos[i].top,
        left: pos[i].left,
        size: pickSize(),
        opacity: 0,
        driftX: randBetween(-10, 10),
        driftY: randBetween(-10, 10),
        duration: randBetween(6, 10),
      }))
    );
  }, []);

  useEffect(() => {
    if (hexes.length === 0) return;
    cycleRef.current = (idx: number) => {
      setHexes((prev) => {
        const next = [...prev];
        next[idx] = { ...next[idx], opacity: 0.22 };
        return next;
      });
      const holdId = window.setTimeout(() => {
        setHexes((prev) => {
          const next = [...prev];
          next[idx] = { ...next[idx], opacity: 0 };
          return next;
        });
        const repositionId = window.setTimeout(() => {
          const edgePool = generateEdgeBiasedPositions(4);
          const pos =
            Math.random() < 0.5
              ? edgePool[Math.floor(randBetween(0, edgePool.length))]
              : randomPositionAvoidCenter();
          setHexes((prev) => {
            const next = [...prev];
            next[idx] = {
              ...next[idx],
              top: pos.top,
              left: pos.left,
              size: pickSize(),
              driftX: randBetween(-10, 10),
              driftY: randBetween(-10, 10),
              duration: randBetween(6, 10),
            };
            return next;
          });
          cycleRef.current(idx);
        }, 900);
        timersRef.current.set(idx, repositionId);
      }, 2400);
      timersRef.current.set(idx, holdId);
    };
    for (let i = 0; i < hexes.length; i++) {
      const startDelay = Math.floor(randBetween(0, 1000));
      const id = window.setTimeout(() => cycleRef.current(i), startDelay);
      timersRef.current.set(i, id);
    }
    return () => {
      timersRef.current.forEach((id) => window.clearTimeout(id));
      timersRef.current.clear();
    };
  }, [hexes.length]);

  return (
    <div
      className="absolute inset-0 z-0 pointer-events-none"
      style={{
        transform: `translate(${offsetX}px, ${offsetY}px)`,
        transition: 'transform 300ms ease-out',
        willChange: 'transform',
      }}
    >
      {hexes.map((h) => {
        const hexHeight = h.size * 0.866;
        return (
          <div
            key={h.id}
            className="absolute"
            style={{
              top: `${h.top}%`,
              left: `${h.left}%`,
              width: h.size,
              height: hexHeight,
              marginTop: -(hexHeight / 2),
              marginLeft: -(h.size / 2),
            }}
          >
            <style jsx key={`drift-${h.id}`}>{`
              @keyframes drift-${h.id} {
                from { transform: translate(0px, 0px); }
                to { transform: translate(${h.driftX}px, ${h.driftY}px); }
              }
            `}</style>
            <div
              className="absolute inset-0"
              style={{
                filter: "blur(4px)",
                opacity: h.opacity,
                transition: "opacity 800ms ease",
                animation: `drift-${h.id} ${h.duration}s ease-in-out infinite alternate`,
              }}
            >
              <div className="clip-hex bg-emerald-500/18 w-full h-full" />
            </div>
            <div
              className="absolute inset-0"
              style={{
                opacity: h.opacity,
                transition: "opacity 800ms ease",
                animation: `drift-${h.id} ${h.duration}s ease-in-out infinite alternate`,
              }}
            >
              <div className="clip-hex border border-emerald-400/20 w-full h-full" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
