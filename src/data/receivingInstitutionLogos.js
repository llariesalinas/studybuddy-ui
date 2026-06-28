// Studybuddy-owned Receiving Institution -> domain mapping for logo.dev (see ADR-0002).
// PayMongo's receiving-institutions response has no logo field, so brand marks are
// resolved client-side via img.logo.dev/{domain} using this mapping. Keyed by a
// normalized institution name because PayMongo's institution `id` values are opaque
// per-account identifiers, not stable codes -- name is the only field guaranteed to
// match across PayMongo accounts/environments.
//
// Coverage: major InstaPay-participating banks and e-wallets known to appear in
// PayMongo's receiving-institutions list. This is not yet a verified 1:1 match against
// PayMongo's full ~90-entry list -- institutions without an entry here simply fall back
// to the generic bank/phone icon (see getReceivingInstitutionLogoUrl below), so adding
// more entries as they're observed in production is always safe.
export const RECEIVING_INSTITUTION_LOGO_DOMAINS = {
  'gcash': 'gcash.com',
  'maya': 'maya.ph',
  'paymaya': 'maya.ph',
  'grabpay': 'grab.com',
  'shopeepay': 'shopeepay.ph',
  'coins.ph': 'coins.ph',

  'bdo unibank': 'bdo.com.ph',
  'bdo unibank, inc.': 'bdo.com.ph',
  'bdo': 'bdo.com.ph',
  'bank of the philippine islands': 'bpi.com.ph',
  'bpi': 'bpi.com.ph',
  'metropolitan bank and trust company': 'metrobank.com.ph',
  'metrobank': 'metrobank.com.ph',
  'land bank of the philippines': 'landbank.com',
  'landbank': 'landbank.com',
  'philippine national bank': 'pnb.com.ph',
  'pnb': 'pnb.com.ph',
  'rizal commercial banking corporation': 'rcbc.com',
  'rcbc': 'rcbc.com',
  'security bank corporation': 'securitybank.com',
  'security bank': 'securitybank.com',
  'china banking corporation': 'chinabank.ph',
  'chinabank': 'chinabank.ph',
  'eastwest bank': 'eastwestbanker.com',
  'east west banking corporation': 'eastwestbanker.com',
  'union bank of the philippines': 'unionbankph.com',
  'unionbank': 'unionbankph.com',
  'philippine savings bank': 'psbank.com.ph',
  'psbank': 'psbank.com.ph',
  'asia united bank': 'aub.com.ph',
  'aub': 'aub.com.ph',
  'robinsons bank corporation': 'robinsonsbank.com.ph',
  'robinsons bank': 'robinsonsbank.com.ph',
  'sterling bank of asia': 'sterlingbankasia.com',
  'maybank philippines': 'maybank.com.ph',
  'maybank': 'maybank.com.ph',
  'united coconut planters bank': 'ucpb.com',
  'ucpb': 'ucpb.com',
  'development bank of the philippines': 'dbp.ph',
  'dbp': 'dbp.ph',
  'citibank': 'citi.com',
  'hsbc': 'hsbc.com.ph',
  'standard chartered bank': 'sc.com',
  'standard chartered': 'sc.com',
  'ing bank': 'ing.com.ph',
  'cimb bank philippines': 'cimbbank.com.ph',
  'cimb': 'cimbbank.com.ph',
  'tonik digital bank': 'tonikbank.com',
  'tonik': 'tonikbank.com',
  'gotyme bank': 'gotyme.com.ph',
  'gotyme': 'gotyme.com.ph',
  'seabank philippines': 'seabank.ph',
  'seabank': 'seabank.ph',
  'uno digital bank': 'uno.bank',
  'unobank': 'uno.bank',
  'komo': 'komo.ph',
}

const normalizeInstitutionName = (name) =>
  String(name || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')

export const LOGO_DEV_IMAGE_BASE_URL = 'https://img.logo.dev'

export function getReceivingInstitutionLogoUrl(institution, token = '') {
  const name = normalizeInstitutionName(institution?.name)
  const domain = RECEIVING_INSTITUTION_LOGO_DOMAINS[name]
  if (!domain) return null

  return token
    ? `${LOGO_DEV_IMAGE_BASE_URL}/${domain}?token=${token}`
    : `${LOGO_DEV_IMAGE_BASE_URL}/${domain}`
}
