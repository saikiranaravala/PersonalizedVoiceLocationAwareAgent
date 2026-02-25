import React, { forwardRef } from 'react';
import './Button.css';

/**
 * Button Component
 * 
 * Production-grade button with full accessibility support
 * Follows Apple HIG and WCAG AAA guidelines
 * 
 * Features:
 * - Multiple variants (primary, secondary, ghost, danger)
 * - Sizes (sm, base, lg, xl)
 * - Icon support
 * - Loading states
 * - Full keyboard navigation
 * - Haptic feedback ready
 */

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual variant of the button */
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  
  /** Size of the button */
  size?: 'sm' | 'base' | 'lg' | 'xl';
  
  /** Full width button */
  fullWidth?: boolean;
  
  /** Icon to display before text */
  iconBefore?: React.ReactNode;
  
  /** Icon to display after text */
  iconAfter?: React.ReactNode;
  
  /** Icon only button (no text) */
  iconOnly?: React.ReactNode;
  
  /** Loading state */
  loading?: boolean;
  
  /** Disabled state */
  disabled?: boolean;
  
  /** ARIA label for screen readers */
  'aria-label'?: string;
  
  /** Children (button text) */
  children?: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'base',
      fullWidth = false,
      iconBefore,
      iconAfter,
      iconOnly,
      loading = false,
      disabled = false,
      className = '',
      children,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;
    
    const buttonClasses = [
      'button',
      `button--${variant}`,
      `button--${size}`,
      fullWidth && 'button--full-width',
      iconOnly && 'button--icon-only',
      loading && 'button--loading',
      className,
    ]
      .filter(Boolean)
      .join(' ');

    // For icon-only buttons, require aria-label
    if (iconOnly && !props['aria-label']) {
      console.warn('Button: Icon-only buttons must have an aria-label for accessibility');
    }

    return (
      <button
        ref={ref}
        type={type}
        className={buttonClasses}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <span className="button__spinner" aria-hidden="true">
            <svg
              className="button__spinner-icon"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                className="button__spinner-circle"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                strokeLinecap="round"
              />
            </svg>
          </span>
        )}
        
        {!loading && iconBefore && (
          <span className="button__icon button__icon--before" aria-hidden="true">
            {iconBefore}
          </span>
        )}
        
        {!loading && iconOnly && (
          <span className="button__icon button__icon--only" aria-hidden="true">
            {iconOnly}
          </span>
        )}
        
        {!iconOnly && children && (
          <span className="button__text">{children}</span>
        )}
        
        {!loading && iconAfter && (
          <span className="button__icon button__icon--after" aria-hidden="true">
            {iconAfter}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
