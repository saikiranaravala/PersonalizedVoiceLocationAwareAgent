/**
 * Profile Settings Component
 * Allows users to edit profile or reset all data
 */

import React, { useState } from 'react';
import { UserProfile } from '../../types/userProfile';
import './ProfileSettings.css';

interface ProfileSettingsProps {
  profile: UserProfile;
  onUpdate: (profile: Partial<UserProfile>) => void;
  onReset: () => void;
  onClose: () => void;
}

export const ProfileSettings: React.FC<ProfileSettingsProps> = ({
  profile,
  onUpdate,
  onReset,
  onClose,
}) => {
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [formData, setFormData] = useState({
    firstName: profile.firstName,
    lastName: profile.lastName || '',
    gender: profile.gender,
    age: profile.age?.toString() || '',
    title: profile.title,
    address: profile.address || '',  // NEW: Include address
    city: profile.city,
    state: profile.state,
    country: profile.country,
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    const age = formData.age ? parseInt(formData.age) : undefined;
    
    onUpdate({
      firstName: formData.firstName,
      lastName: formData.lastName || undefined,
      gender: formData.gender as any,
      age,
      title: formData.title as any,
      address: formData.address || undefined,  // NEW: Include address
      city: formData.city,
      state: formData.state,
      country: formData.country,
    });
    
    onClose();
  };

  const handleReset = () => {
    onReset();
    setShowResetConfirm(false);
  };

  if (showResetConfirm) {
    return (
      <div className="profile-settings-overlay" onClick={onClose}>
        <div className="profile-settings-modal profile-settings-modal--confirm" onClick={(e) => e.stopPropagation()}>
          <div className="confirm-header">
            <span className="confirm-icon">⚠️</span>
            <h2 className="confirm-title">Reset All Data?</h2>
          </div>
          
          <div className="confirm-content">
            <p className="confirm-text">
              This will permanently delete:
            </p>
            <ul className="confirm-list">
              <li>Your profile information</li>
              <li>All restaurant visit history</li>
              <li>All Uber trip history</li>
              <li>Learned preferences and patterns</li>
            </ul>
            <p className="confirm-warning">
              <strong>This action cannot be undone.</strong>
            </p>
          </div>

          <div className="confirm-footer">
            <button
              onClick={() => setShowResetConfirm(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleReset}
              className="btn btn-danger"
            >
              Yes, Reset Everything
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-settings-overlay" onClick={onClose}>
      <div className="profile-settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="profile-settings-header">
          <h2 className="profile-settings-title">Profile Settings</h2>
          <button
            onClick={onClose}
            className="close-button"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <div className="profile-settings-content">
          {/* Basic Info */}
          <div className="settings-section">
            <h3 className="section-title">Basic Information</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-firstName">First Name</label>
                <input
                  id="edit-firstName"
                  type="text"
                  value={formData.firstName}
                  onChange={(e) => handleInputChange('firstName', e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit-lastName">Last Name</label>
                <input
                  id="edit-lastName"
                  type="text"
                  value={formData.lastName}
                  onChange={(e) => handleInputChange('lastName', e.target.value)}
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-gender">Gender</label>
                <select
                  id="edit-gender"
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
                <label htmlFor="edit-age">Age</label>
                <input
                  id="edit-age"
                  type="number"
                  value={formData.age}
                  onChange={(e) => handleInputChange('age', e.target.value)}
                  min="1"
                  max="120"
                  className="form-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="edit-title">Title</label>
              <select
                id="edit-title"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
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

          {/* Location */}
          <div className="settings-section">
            <h3 className="section-title">Location</h3>
            
            <div className="form-group">
              <label htmlFor="edit-address">Street Address</label>
              <input
                id="edit-address"
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
              <label htmlFor="edit-city">City</label>
              <input
                id="edit-city"
                type="text"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
                className="form-input"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="edit-state">State/Province</label>
                <input
                  id="edit-state"
                  type="text"
                  value={formData.state}
                  onChange={(e) => handleInputChange('state', e.target.value)}
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="edit-country">Country</label>
                <input
                  id="edit-country"
                  type="text"
                  value={formData.country}
                  onChange={(e) => handleInputChange('country', e.target.value)}
                  className="form-input"
                />
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="settings-section settings-section--danger">
            <h3 className="section-title">Danger Zone</h3>
            <div className="danger-zone">
              <div className="danger-zone-content">
                <h4 className="danger-zone-title">Reset All Data</h4>
                <p className="danger-zone-description">
                  Delete your profile, history, and all preferences. This action cannot be undone.
                </p>
              </div>
              <button
                onClick={() => setShowResetConfirm(true)}
                className="btn btn-danger-outline"
              >
                Reset Everything
              </button>
            </div>
          </div>
        </div>

        <div className="profile-settings-footer">
          <button
            onClick={onClose}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};
