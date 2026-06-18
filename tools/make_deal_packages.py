#!/usr/bin/env python3
"""
Paragon deal-package generators.
Two write-ups per deal, opposite framing:
  build_buyer_package(d)  -> sell/assign a deal to a CASH BUYER (shows upside)
  build_seller_package(d) -> negotiate a LOW offer with SELLER/AGENT (shows downside)
Edit the DEAL dicts at the bottom and run:  python3 tools/make_deal_packages.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

NAVY=colors.HexColor('#2E4057'); GOLD=colors.HexColor('#E0A600'); LT=colors.HexColor('#F4F6F8')
ss=getSampleStyleSheet()
def S(n,**k): return ParagraphStyle(n, parent=ss['Normal'], **k)
TITLE=S('t',fontSize=22,textColor=NAVY,leading=24,spaceAfter=4,alignment=TA_CENTER)
SUBT =S('s',fontSize=11,textColor=colors.grey,alignment=TA_CENTER,spaceAfter=12)
H2   =S('h2',fontSize=13,textColor=NAVY,spaceBefore=12,spaceAfter=5,leading=15)
BODY =S('b',fontSize=10,leading=14,alignment=TA_JUSTIFY,spaceAfter=6)
SMALL=S('sm',fontSize=7.5,textColor=colors.grey,leading=9.5)
CELL =S('c',fontSize=9,leading=11)
CELLB=S('cb',fontSize=9,leading=11,textColor=colors.white)
BIGNUM=S('bn',fontSize=18,textColor=NAVY,alignment=TA_CENTER,leading=20)
BIGLBL=S('bl',fontSize=7.5,textColor=colors.grey,alignment=TA_CENTER,leading=9)

PARAGON='Paragon Government Solutions LLC'
CONTACT='Charles Pleasant, Manager · 888-495-6935 · charles@paragongovsolutions.net'

def brandbar():
    t=Table([['']],colWidths=[7.0*inch]); t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),1.4,GOLD)])); return t

def stat_row(items):
    data=[[Paragraph(v,BIGNUM) for v,l in items],[Paragraph(l,BIGLBL) for v,l in items]]
    t=Table(data,colWidths=[7.0*inch/len(items)]*len(items))
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),LT),('BOX',(0,0),(-1,-1),0.5,colors.lightgrey),
        ('INNERGRID',(0,0),(-1,-1),0.5,colors.white),('TOPPADDING',(0,0),(-1,-1),8),
        ('BOTTOMPADDING',(0,0),(-1,-1),8)])); return t

def tbl(header, rows, widths):
    data=[[Paragraph(h,CELLB) for h in header]]+[[Paragraph(str(c),CELL) for c in r] for r in rows]
    t=Table(data,colWidths=widths,repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,LT]),
        ('GRID',(0,0),(-1,-1),0.4,colors.lightgrey),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
        ('LEFTPADDING',(0,0),(-1,-1),5)])); return t

def header_block(story, kicker, addr, sub):
    story.append(Paragraph(PARAGON, S('p',fontSize=9,textColor=NAVY,alignment=TA_CENTER)))
    story.append(brandbar()); story.append(Spacer(1,10))
    story.append(Paragraph(kicker, TITLE))
    story.append(Paragraph(addr, S('a',fontSize=13,textColor=GOLD,alignment=TA_CENTER,spaceAfter=2)))
    story.append(Paragraph(sub, SUBT))

def footer(story, disclaimer):
    story.append(Spacer(1,10)); story.append(brandbar())
    story.append(Paragraph(CONTACT, S('f',fontSize=8.5,textColor=NAVY,alignment=TA_CENTER,spaceBefore=4)))
    story.append(Paragraph(disclaimer, SMALL))

# ---------------------------------------------------------------- BUYER PACKAGE
def build_buyer_package(d, out):
    doc=SimpleDocTemplate(out,pagesize=letter,topMargin=0.6*inch,bottomMargin=0.6*inch,
        leftMargin=0.75*inch,rightMargin=0.75*inch)
    s=[]
    header_block(s,'CASH BUYER OPPORTUNITY',d['address'],
        f"{d['neighborhood']} · Prepared {d['date']} · Cash assignment / wholesale")
    s.append(stat_row([(f"${d['buyer_price']:,}","YOUR PRICE"),(f"${d['arv']:,}","EST. ARV"),
        (f"${d['repairs']:,}","EST. REPAIRS"),(f"${d['rent']:,}/mo","IN-PLACE RENT")]))
    s.append(Spacer(1,10))
    s.append(Paragraph('Investment Thesis',H2))
    s.append(Paragraph(d['thesis'],BODY))
    allin=d['buyer_price']+d['repairs']
    equity=d['arv']-allin
    s.append(Paragraph('The Numbers',H2))
    s.append(tbl(['Metric','Value'],[
        ['Your acquisition price (assignable contract)',f"${d['buyer_price']:,}"],
        ['Estimated repairs (cosmetic/refresh)',f"${d['repairs']:,}"],
        ['All-in cost',f"${allin:,}"],
        ['Conservative ARV',f"${d['arv']:,}  (range ${d['arv_low']:,}–${d['arv_high']:,})"],
        ['Built-in equity at ARV',f"${equity:,}"],
        ['In-place rent / stabilized',f"${d['rent']:,}/mo  →  ${d['rent_stab']:,}/mo"],
        ['Est. cap rate (in-place / stabilized)',f"{d['cap']} / {d['cap_stab']}"],
    ],[3.6*inch,3.4*inch]))
    s.append(Paragraph('Key Facts',H2))
    s.append(tbl(['Item','Detail'],d['facts'],[2.2*inch,4.8*inch]))
    s.append(PageBreak())
    header_block(s,'COMPARABLES & CONDITION',d['address'],f"Prepared {d['date']}")
    s.append(Paragraph('Comparable Sales',H2))
    s.append(tbl(['Address','Sold','Price','Bd/Ba','SqFt'],d['comps'],
        [2.5*inch,1.0*inch,1.1*inch,0.9*inch,1.5*inch]))
    s.append(Paragraph('Repair Scope (planning allowance, not a bid)',H2))
    s.append(tbl(['Scope','Budget'],d['repair_items'],[4.6*inch,2.4*inch]))
    s.append(Paragraph('Exit Strategies',H2))
    for e in d['exits']: s.append(Paragraph('• '+e,BODY))
    footer(s,d['disclaimer'])
    doc.build(s); print('wrote',out)

# --------------------------------------------------------------- SELLER PACKAGE
def build_seller_package(d, out):
    doc=SimpleDocTemplate(out,pagesize=letter,topMargin=0.6*inch,bottomMargin=0.6*inch,
        leftMargin=0.75*inch,rightMargin=0.75*inch)
    s=[]
    header_block(s,'CASH OFFER SUMMARY',d['address'],
        f"Prepared for {d['agent']} · {d['date']} · {PARAGON} (Buyer)")
    s.append(stat_row([(f"${d['offer']:,}","OUR CASH OFFER"),("AS-IS","CONDITION"),
        (d['close'],"CLOSE"),("$0","SELLER REPAIRS/FEES")]))
    s.append(Spacer(1,10))
    s.append(Paragraph('Why This Offer Works for the Seller',H2))
    s.append(Paragraph(d['why'],BODY))
    # Net-sheet comparison
    s.append(Paragraph('Seller Net Comparison: Retail Listing vs. Our Cash Offer',H2))
    s.append(tbl(['Line item','Retail listing','Our cash offer'],d['netsheet'],
        [3.0*inch,2.0*inch,2.0*inch]))
    s.append(Paragraph(d['net_note'],SMALL))
    s.append(PageBreak())
    header_block(s,'OFFER JUSTIFICATION',d['address'],f"Prepared for {d['agent']} · {d['date']}")
    s.append(Paragraph('Condition & Repair Deductions',H2))
    s.append(Paragraph('The property is purchased strictly as-is. Our price reflects the following '
        'estimated costs a cash buyer must absorb:',BODY))
    s.append(tbl(['Repair / cost item','Estimated cost'],d['repairs_list'],[4.6*inch,2.4*inch]))
    s.append(Paragraph('Supporting Comparable Sales',H2))
    s.append(tbl(['Address','Sold','Price','Notes'],d['comps'],
        [2.3*inch,1.0*inch,1.1*inch,2.6*inch]))
    s.append(Paragraph('Our Terms',H2))
    for t in d['terms']: s.append(Paragraph('• '+t,BODY))
    footer(s,d['disclaimer'])
    doc.build(s); print('wrote',out)

# ======================= DEAL DATA (edit per deal) =======================
SEVEN512_BUYER = {
 'address':'7512 S Saint Lawrence Ave, Chicago, IL 60619',
 'neighborhood':'Greater Grand Crossing / Park Manor (60619)',
 'date':'June 17, 2026',
 'buyer_price':114000,'arv':180000,'arv_low':170000,'arv_high':190000,
 'repairs':25000,'rent':1500,'rent_stab':1800,'cap':'8.7%','cap_stab':'9.1%',
 'thesis':('Tenant-occupied brick bungalow with immediate income, detached garage, two full baths '
   'and a full basement. Reportedly remodeled in 2020 and functional; finishes are dated and there '
   'is no central cooling. Best use is a buy-and-hold or light value-add — at this assignment price '
   'the all-in basis sits well below ARV, leaving real equity or a strong day-one cash-flow play.'),
 'facts':[['Property type','Detached single-family brick bungalow'],
   ['Configuration','3 bed / 2 full bath (verify legal bed/bath)'],
   ['Living area','960 sq ft above grade + full basement'],
   ['Parking','1-car detached garage'],
   ['Occupancy','Tenant-occupied, month-to-month at $1,500/mo'],
   ['Heating / cooling','Floor furnace / no central cooling'],
   ['Year built / rehab','1914 / major remodel reported 2020'],
   ['Taxes (2023)','$1,582'],['Zoning / APN','RS-2 / 20-27-403-027-0000']],
 'comps':[['7237 S St Lawrence Ave','05/29/26','$194,000','3/1.5','1,250'],
   ['7443 S Wabash Ave','04/24/26','$185,000','3/1','1,200'],
   ['8446 S King Dr','03/31/26','$175,000','3/2','1,000'],
   ['7532 S Saint Lawrence Ave','05/20/26','$170,000','3/2','1,438'],
   ['7139 S Dobson Ave','04/24/26','$149,900','2/1','1,200']],
 'repair_items':[['Interior paint, patching & trim','$4,000'],['Flooring / carpentry repairs','$2,500'],
   ['Kitchen refresh','$5,500'],['Two bathroom refreshes','$4,500'],['Lighting / electrical trim','$1,500'],
   ['Basement cleanup / moisture','$3,000'],['Exterior, yard & garage','$1,500'],
   ['Final clean, permits & contingency','$2,500'],['BASE TOTAL','$25,000']],
 'exits':[('BUY-AND-HOLD (best fit): immediate $1,500/mo rent, path to $1,800 after refresh — '
   '~8.7% in-place cap at the $114,000 price, ~9.1% stabilized on all-in.'),
   'LIGHT VALUE-ADD: cosmetic refresh, raise rents, refinance or resell to a retail buyer.',
   'Note: not underwritten for a deep retail flip given the 960 sf above-grade footprint.'],
 'disclaimer':('Investor analysis only — figures are planning estimates from listing data, recent sales '
   'and visible-condition assumptions. No onsite inspection, contractor bid, sewer scope or mechanical '
   'testing performed. Buyer to independently verify ARV, repairs, permits, legal bed/bath, title, tenant '
   'status and all financials before relying on this package. Sold AS-IS. Do not disturb the tenant.'),
}

TIDEWATER_SELLER = {
 'address':'3403 Tidewater Dr, Houston, TX 77045',
 'agent':'John Williams, Real Estate Options of Texas',
 'date':'June 17, 2026','offer':138000,'close':'~21 days',
 'why':('Paragon is a direct cash buyer purchasing as-is — no financing, no appraisal, no inspection '
   'repair demands, and no agent commission owed by the seller on our side. On an REO that has been '
   'marketed 44 days, our offer delivers speed and certainty of close, which often nets the bank more '
   'than a higher financed offer that risks falling through. Our price reflects the as-is condition and '
   'the cost a cash buyer must absorb to bring the home to market.'),
 'netsheet':[['Sale price','$159,000 (list)','$138,000 (cash)'],
   ['Agent commission (~6%)','-$9,540','$0 (buyer side)'],
   ['Seller-paid repairs / concessions','-$8,000 (typical)','$0'],
   ['Holding / carrying (60–90+ days)','-$3,500','$0 (fast close)'],
   ['Financing fall-through risk','High','None (cash)'],
   ['Est. net to seller','~$137,960','$138,000'],
   ['Time to close','60–120+ days','~21 days']],
 'net_note':('Illustrative net comparison — actual figures vary. The point: a clean cash offer can net '
   'the seller a comparable amount far faster and with no risk of buyer financing collapse.'),
 'repairs_list':[['Interior paint / cosmetic refresh','$6,000'],['Flooring repairs','$3,000'],
   ['Kitchen / bath updates','$6,000'],['HVAC service / mechanical check','$3,000'],
   ['Turn / make-ready / clean','$2,000'],['Holding, taxes & contingency','$5,000'],
   ['Estimated buyer cost to absorb','~$25,000']],
 'comps':[['3347 Tidewater Dr','—','$176,700','Off-market value, larger'],
   ['5535 Elmlawn Dr','active','$155,000','3/2 comparable'],
   ['5125 Ricky St','active','$159,000','3/1 needs work'],
   ['As-is Zestimate (subject)','—','$153,800','Reflects current condition']],
 'terms':['All cash — no financing or appraisal contingency','Purchase strictly AS-IS, WHERE-IS',
   'Close in ~21 days on buyer’s title company','Proof of funds provided',
   'Buyer covers standard buyer closing costs','Buyer: Paragon Government Solutions LLC, and/or assigns'],
 'disclaimer':('Prepared by Paragon Government Solutions LLC (Buyer) to support a cash offer. Estimates are '
   'for negotiation reference only and are not an appraisal. All figures subject to verification.'),
}

if __name__=='__main__':
    build_buyer_package(SEVEN512_BUYER,'7512_Cash_Buyer_Package_Paragon.pdf')
    build_seller_package(TIDEWATER_SELLER,'3403_Tidewater_Seller_Offer_Package.pdf')
