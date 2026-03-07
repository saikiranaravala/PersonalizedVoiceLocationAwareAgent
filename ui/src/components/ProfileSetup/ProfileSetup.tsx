/**
 * User Profile Setup Modal
 */

import React, { useState } from 'react';
import { Gender, Title } from '../../types/userProfile';
import './ProfileSetup.css';

interface ProfileSetupProps {
  onComplete: (profile: {
    firstName: string;
    lastName?: string;
    gender: Gender;
    age?: number;
    title?: Title;
    address?: string;  // NEW: Complete street address
    city: string;
    state: string;
    country: string;
  }) => void;
  onSkip?: () => void;
}

export const ProfileSetup: React.FC<ProfileSetupProps> = ({ onComplete, onSkip }) => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    gender: 'prefer-not-to-say' as Gender,
    age: '',
    customTitle: '' as Title,
    address: '',  // NEW: Street address
    city: 'Erie',
    state: 'Pennsylvania',
    country: 'US',
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (step < 3) {
      setStep(step + 1);
    } else {
      // Submit
      const age = formData.age ? parseInt(formData.age) : undefined;
      
      onComplete({
        firstName: formData.firstName,
        lastName: formData.lastName || undefined,
        gender: formData.gender,
        age,
        title: formData.customTitle || undefined,
        address: formData.address || undefined,  // NEW: Include address
        city: formData.city,
        state: formData.state,
        country: formData.country,
      });
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const canProceed = () => {
    if (step === 1) {
      return formData.firstName.trim().length > 0;
    }
    if (step === 3) {
      return formData.city.trim().length > 0;
    }
    return true;
  };

  return (
    <div className="profile-setup-overlay">
      <div className="profile-setup-modal">
        <div className="profile-setup-header">
          <h2 className="profile-setup-title">Welcome! Let's Get to Know You</h2>
          <p className="profile-setup-subtitle">
            This helps me provide personalized assistance
          </p>
          <div className="profile-setup-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${(step / 3) * 100}%` }}
              />
            </div>
            <span className="progress-text">Step {step} of 3</span>
          </div>
        </div>

        <div className="profile-setup-content">
          {/* Step 1: Basic Info */}
          {step === 1 && (
            <div className="profile-step">
              <h3 className="step-title">What's your name?</h3>
              
              <div className="form-group">
                <label htmlFor="firstName">First Name *</label>
                <input
                  id="firstName"
                  type="text"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange('firstName', e.target.value)}
                  placeholder="Jack"
                  autoFocus
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="lastName">Last Name (Optional)</label>
                <input
                  id="lastName"
                  type="text"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange('lastName', e.target.value)}
                  placeholder="Smith"
                  className="form-input"
                />
              </div>
            </div>
          )}

          {/* Step 2: Personal Details */}
          {step === 2 && (
            <div className="profile-step">
              <h3 className="step-title">A few more details</h3>
              
              <div className="form-group">
                <label htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  value={formData.gender}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                  className="form-select"
                >
                  <option value="prefer-not-to-say">Prefer not to say</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="age">Age (Optional)</label>
                <input
                  id="age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  placeholder="25"
                  min="1"
                  max="120"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="title">Title (Optional)</label>
                <select
                  id="title"
                  value={formData.customTitle}
                  onChange={(e) => handleInputChange('customTitle', e.target.value)}
                  className="form-select"
                >
                  <option value="">Auto (based on gender/age)</option>
                  <option value="Mr.">Mr.</option>
                  <option value="Mrs.">Mrs.</option>
                  <option value="Ms.">Ms.</option>
                  <option value="Miss">Miss</option>
                  <option value="Dr.">Dr.</option>
                  <option value="Master">Master</option>
                </select>
              </div>
            </div>
          )}

          {/* Step 3: Location */}
          {step === 3 && (
            <div className="profile-step">
              <h3 className="step-title">Where are you located?</h3>
              
              <div className="form-group">
                <label htmlFor="address">Street Address (Optional)</label>
                <input
                  id="address"
                  type="text"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  placeholder="123 Main Street, Apt 4B"
                  className="form-input"
                />
                <span className="form-help-text">
                  Used for Uber pickup on desktop. Leave blank to use your city.
                </span>
              </div>
              
              <div className="form-group">
                <label htmlFor="city">City *</label>
                <input
                  id="city"
                  type="text"
                  value={formData.city}
                  onChange={(e) => handleInputChange('city', e.target.value)}
                  placeholder="Erie"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="state">State/Province</label>
                <input
                  id="state"
                  type="text"
                  value={formData.state}
                  onChange={(e) => handleInputChange('state', e.target.value)}
                  placeholder="Pennsylvania"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="country">Country</label>
                <input
                  id="country"
                  type="text"
                  value={formData.country}
                  onChange={(e) => handleInputChange('country', e.target.value)}
                  placeholder="US"
                  className="form-input"
                />
              </div>

              <div className="info-box">
                <span className="info-icon">ℹ️</span>
                <p className="info-text">
                  This helps me provide location-specific recommendations for restaurants,
                  weather, and rides.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className="profile-setup-footer">
          <div className="button-group">
            {step > 1 && (
              <button
                onClick={handleBack}
                className="btn btn-secondary"
              >
                Back
              </button>
            )}
            
            {onSkip && step === 1 && (
              <button
                onClick={onSkip}
                className="btn btn-ghost"
              >
                Skip for now
              </button>
            )}
          </div>

          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="btn btn-primary"
          >
            {step === 3 ? 'Complete Setup' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  );
};
