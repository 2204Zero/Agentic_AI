"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";

type Hex = {
  id: number;
  top: number;
  left: number;
  size: number;
  opacity: number;
};

const SIZES = [40, 60, 80];
const MIN_PAD = 10;
const MAX_PAD = 90;
const MIN_DISTANCE = 15;
const HEX_COUNT = 6;

function randBetween(min: number, max: number) {
  return Math.random() * (max - min) + min;
}

function pickSize() {
  return SIZES[Math.floor(Math.random() * SIZES.length)];
}

function distance(a: { top: number; left: number }, b: { top: number; left: number }) {
  const dx = a.left - b.left;
  const dy = a.top - b.top;
  return Math.sqrt(dx * dx + dy * dy);
}

function generatePositions(count: number) {
  const points: Array<{ top: number; left: number }> = [];
  for (let i = 0; i < count; i++) {
    let tries = 0;
    let p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
    while (tries < 30 && points.some((q) => distance(p, q) < MIN_DISTANCE)) {
      p = { top: randBetween(MIN_PAD, MAX_PAD), left: randBetween(MIN_PAD, MAX_PAD) };
      tries++;
    }
    points.push(p);
  }
  return points;
}

export default function HexGrid() {
  const initial = useMemo(() => {
    const pos = generatePositions(HEX_COUNT);
    return Array.from({ length: HEX_COUNT }).map((_, i) => ({
      id: i,
      top: pos[i].top,
      left: pos[i].left,
      size: pickSize(),
      opacity: 0,
    })) as Hex[];
  }, []);

  const [hexes, setHexes] = useState<Hex[]>(initial);
  const timersRef = useRef<Map<number, number>>(new Map());
  const cycleRef = useRef<(idx: number) => void>(() => {});

  useEffect(() => {
    cycleRef.current = (idx: number) => {
      setHexes((prev) => {
        const next = [...prev];
        next[idx] = { ...next[idx], opacity: 0.25 };
        return next;
      });
      const holdId = window.setTimeout(() => {
        setHexes((prev) => {
          const next = [...prev];
          next[idx] = { ...next[idx], opacity: 0 };
          return next;
        });
        const repositionId = window.setTimeout(() => {
          const pos = generatePositions(1)[0];
          setHexes((prev) => {
            const next = [...prev];
            next[idx] = { ...next[idx], top: pos.top, left: pos.left, size: pickSize() };
            return next;
          });
          cycleRef.current(idx);
        }, 800);
        timersRef.current.set(idx, repositionId);
      }, 2200);
      timersRef.current.set(idx, holdId);
    };
    for (let i = 0; i < HEX_COUNT; i++) {
      const startDelay = Math.floor(randBetween(0, 1000));
      const id = window.setTimeout(() => cycleRef.current(i), startDelay);
      timersRef.current.set(i, id);
    }
    return () => {
      timersRef.current.forEach((id) => window.clearTimeout(id));
      timersRef.current.clear();
    };
  }, []);

  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
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
            <div
              className="absolute inset-0"
              style={{
                filter: "blur(12px)",
                opacity: h.opacity,
                transition: "opacity 800ms ease",
              }}
            >
              <div className="clip-hex bg-emerald-500/10 glow-emerald w-full h-full" />
            </div>
            <div
              className="absolute inset-0"
              style={{
                opacity: h.opacity,
                transition: "opacity 800ms ease",
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
