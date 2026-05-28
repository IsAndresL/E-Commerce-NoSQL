import React from "react";

const Svg = ({ children, className = "", viewBox = "0 0 24 24" }) => (
  <svg className={className} viewBox={viewBox} fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
    {children}
  </svg>
);

export const IconBrand = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M6 7V6a6 6 0 0112 0v1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M4 7h16l-1.2 11.2A2 2 0 0116.8 20H7.2a2 2 0 01-1.98-1.8L4 7z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconSearch = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M21 21l-4.35-4.35" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="11" cy="11" r="6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconCart = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M6 6h15l-1.5 9h-12L6 6z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="10" cy="20" r="1" fill="currentColor"/>
    <circle cx="18" cy="20" r="1" fill="currentColor"/>
  </Svg>
);

export const IconMapPin = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M12 21s7-4.5 7-10a7 7 0 10-14 0c0 5.5 7 10 7 10z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="12" cy="11" r="2" fill="currentColor"/>
  </Svg>
);

export const IconProfile = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="12" cy="7" r="4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconReceipt = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M21 6H3v12h18V6z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M7 9h10M7 13h6" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconCalendar = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M16 3v4M8 3v4M3 11h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconMoney = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <rect x="2" y="6" width="20" height="12" rx="2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M12 9v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="12" cy="12" r="1" fill="currentColor"/>
  </Svg>
);

export const IconBack = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconLogout = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M16 17l5-5-5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M21 12H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconClose = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconTrash = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M3 6h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M8 6v12a2 2 0 002 2h4a2 2 0 002-2V6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M10 11v6M14 11v6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </Svg>
);

export const IconStar = ({ className = "icon" }) => (
  <Svg className={className} viewBox="0 0 24 24">
    <path d="M12 17.27L18.18 21 16.54 13.97 22 9.24 14.81 8.63 12 2 9.19 8.63 2 9.24 7.46 13.97 5.82 21z" fill="currentColor"/>
  </Svg>
);

export default Svg;
