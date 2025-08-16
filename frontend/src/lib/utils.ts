import { clsx, type ClassValue } from "clsx"
import { cva, type VariantProps } from "class-variance-authority"

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}