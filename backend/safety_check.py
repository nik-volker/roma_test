"""Детекция кризиса и опасных safety-ситуаций."""

import logging
import re

logger = logging.getLogger(__name__)

CRISIS_KEYWORDS = [
    "i want to die",
    "i don't want to live",
    "i do not want to live",
    "kill myself",
    "end my life",
    "suicide",
    "self harm",
    "self-harm",
    "убить себя",
    "покончить с собой",
    "свести счёты с жизнью",
    "не хочу жить",
    "давай мне яд",
    "пила таблетки",
    "режу себя",
    "покончу с собой",
    "я не хочу жить",
    "нет смысла жить",
    "хочу умереть",
    "совсем надоело",
    "конец всему",
]


ABUSE_VIOLENCE_PATTERNS = [
    # EN: physical violence and threats
    (
        r"\b(husband|partner|boyfriend|girlfriend|he|she)\s+(hits|hit|beats|beat|punched|pushed)\s+me\b",
        "physical_violence",
    ),
    (
        r"\b(he|she)\s+(hit|beats|beat|punched|pushed|strangled|choked)\s+me\b",
        "physical_violence",
    ),
    (
        r"\b(i am|i'm|im)\s+afraid\s+of\s+(my\s+)?(partner|husband|wife|boyfriend|girlfriend|him|her)\b",
        "fear_for_safety",
    ),
    (r"\b(he|she)\s+(threatens|threatened|is threatening)\s+me\b", "threats"),
    (r"\b(not\s+safe|don't\s+feel\s+safe|do\s+not\s+feel\s+safe)\b", "fear_for_safety"),
    (
        r"\b(he|she)\s+(controls|is controlling)\s+(my\s+)?(phone|money|finances|movements|where\s+i\s+go)\b",
        "coercive_control",
    ),
    (
        r"\b(he|she)\s+(won't|will\s+not|doesn't|does\s+not)\s+let\s+me\s+leave\b",
        "restraining_or_isolation",
    ),
    (r"\b(he|she)\s+(forces|forced|is forcing)\s+me\b", "coercion"),
    # RU: физическое насилие, контроль, угрозы
    (
        r"\b(муж|партнер|парень|девушка|он|она)\s+меня\s+(бьет|бьёт|ударил|ударила|толкнул|толкнула|душил|душила)\b",
        "physical_violence",
    ),
    (
        r"\b(он|она)\s+меня\s+(бьет|бьёт|ударил|ударила|толкнул|толкнула|душил|душила)\b",
        "physical_violence",
    ),
    (
        r"\bя\s+боюсь\s+(мужа|партнера|партнёра|партнершу|партнёршу|его|ее|её|ее)\b",
        "fear_for_safety",
    ),
    (r"\b(он|она)\s+мне\s+угрожает\b", "threats"),
    (
        r"\b(не\s+чувствую\s+себя\s+в\s+безопасности|мне\s+не\s+безопасно)\b",
        "fear_for_safety",
    ),
    (
        r"\b(он|она)\s+контролирует\s+(меня|мой\s+телефон|деньги|мои\s+деньги|мои\s+передвижения|куда\s+я\s+хожу)\b",
        "coercive_control",
    ),
    (r"\b(он|она)\s+не\s+дает\s+уйти\b", "restraining_or_isolation"),
    (r"\b(он|она)\s+меня\s+заставляет\b", "coercion"),
]


FRAUD_FINANCIAL_PATTERNS = [
    # EN: requests to take a loan / borrow money for someone
    (
        r"\b(he|she|they|partner|husband|wife|boyfriend|girlfriend)\s+(asked|asks|wants|told|tells|is asking|is telling)\s+me\s+to\s+(take|get|apply\s+for|sign)\s+(a\s+)?(loan|credit|mortgage)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(take|get|apply\s+for|sign)\s+(a\s+)?(loan|credit|mortgage)\s+for\s+(him|her|them|my\s+(partner|husband|wife|boyfriend|girlfriend))\b",
        "request_to_take_loan",
    ),
    (
        r"\b(he|she|they)\s+(asked|asks|wants|is asking)\s+me\s+to\s+(borrow|lend)\s+(money|cash)\b",
        "request_to_borrow_money",
    ),
    # EN: pressure to transfer money / send money urgently
    (
        r"\b(transfer|send|wire|give)\s+(him|her|them|me)\s+(money|cash|funds)\b",
        "money_transfer_pressure",
    ),
    (
        r"\b(urgent|urgently|right\s+now|immediately)\s+(needs|need)\s+(money|cash|funds)\b",
        "urgent_money_request",
    ),
    # EN: blackmail / extortion / threats for money / scam
    (r"\b(blackmail|blackmailing|blackmailed)\b", "blackmail"),
    (r"\b(extort|extorting|extortion|extorted)\b", "extortion"),
    (r"\b(scam|scammer|scammed|scamming)\b", "scam"),
    (
        r"\b(threatens|threatened|is threatening)\s+(me|to)\s+.*\b(money|leak|share|expose|publish|photos|videos)\b",
        "blackmail_threats",
    ),
    # EN: requests for codes / documents / passwords / banking data
    (
        r"\b(asks?|wants?|demanding|demanded|asked)\s+(me\s+)?(for\s+)?(my\s+)?(verification\s+code|sms\s+code|otp|one[-\s]?time\s+password|banking\s+password|card\s+pin|cvv|card\s+number|passport|id|documents)\b",
        "credential_or_document_request",
    ),
    (
        r"\b(send|share|give)\s+(him|her|them)\s+(my\s+)?(password|verification\s+code|sms\s+code|otp|card\s+pin|cvv|passport|documents)\b",
        "credential_or_document_request",
    ),
    # EN: prison / urgency / pity-based money pressure
    (
        r"\b(he|she|they|my\s+(partner|husband|wife|boyfriend|girlfriend))\s+(is\s+)?in\s+(prison|jail)\b.*\b(money|funds|loan|bail)\b",
        "prison_money_pressure",
    ),
    (
        r"\b(in\s+(prison|jail))\b.*\b(needs?|asks?|wants?)\s+(money|funds|loan)\b",
        "prison_money_pressure",
    ),

    # RU: просьбы взять кредит / занять деньги
    (
        r"\b(он|она|муж|жена|партнер|партнёр|парень|девушка)\s+(просит|просил|просила|хочет|требует|настаивает|заставляет)\s+(меня\s+)?(взять|оформить|подписать|получить)\s+(кредит|займ|заём|ипотеку|ссуду)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(взять|оформить|подписать|получить)\s+(кредит|займ|заём|ипотеку|ссуду)\s+(для|на)\s+(него|неё|нее|них|мужа|жены|партнера|партнёра|парня|девушки)\b",
        "request_to_take_loan",
    ),
    (
        r"\b(он|она)\s+(просит|просил|просила|требует|хочет)\s+(меня\s+)?(занять|одолжить|взять\s+в\s+долг)\s+(деньги|денег|сумму)\b",
        "request_to_borrow_money",
    ),
    # RU: давление на перевод денег
    (
        r"\b(переведи|перевести|отправь|отправить|пришли|прислать|дай|отдай)\s+(ему|ей|им)\s+(деньги|денег|сумму|перевод)\b",
        "money_transfer_pressure",
    ),
    (
        r"\b(срочно|немедленно|прямо\s+сейчас)\s+(нужны|нужна|нужен|надо)\s+(деньги|денег|сумма|перевод)\b",
        "urgent_money_request",
    ),
    # RU: шантаж / вымогательство / мошенничество
    (r"\b(шантаж|шантажирует|шантажировал|шантажировала|шантажируют)\b", "blackmail"),
    (r"\b(вымогает|вымогательство|вымогал|вымогала|вымогают)\b", "extortion"),
    (r"\b(мошенник|мошенница|мошенничество|развод|разводит|кидала|кинул|кинула)\b", "scam"),
    (
        r"\b(угрожает|угрожал|угрожала)\s+.*\b(выложить|опубликовать|разослать|показать|слить)\s+.*\b(фото|видео|переписку|интим)\b",
        "blackmail_threats",
    ),
    # RU: требование кодов / документов / паролей
    (
        r"\b(просит|требует|хочет|просил|просила|требовал|требовала)\s+.*\b(код\s+из\s+смс|смс[-\s]?код|код\s+подтверждения|пароль\s+от|пин[-\s]?код|cvv|cvc|номер\s+карты|данные\s+карты|паспорт|документы)\b",
        "credential_or_document_request",
    ),
    (
        r"\b(отправь|отправить|пришли|прислать|дай|сообщи)\s+(ему|ей|им)\s+(код|пароль|пин|cvv|cvc|данные\s+карты|номер\s+карты|паспорт|документы)\b",
        "credential_or_document_request",
    ),
    # RU: тюрьма + деньги / срочность жалости
    (
        r"\b(он|она|муж|жена|партнер|партнёр|парень|девушка)\s+в\s+(тюрьме|сизо|колонии|зоне)\b.*\b(деньги|денег|кредит|залог|перевод)\b",
        "prison_money_pressure",
    ),
    (
        r"\bв\s+(тюрьме|сизо|колонии|зоне)\b.*\b(нужны|нужна|просит|просил|просила)\s+(деньги|денег|кредит|залог)\b",
        "prison_money_pressure",
    ),
]


# Dangerous-partner / criminal-risk detection.
# Two-phase trigger: a CRIMINAL_CONTEXT match AND at least one of
# (ROMANTIC_INVOLVEMENT | MINIMIZATION | CHILDREN_PRESENT).
# This avoids false positives like discussing a movie or unrelated minor offences.

# Imprisonment / sentencing / release context — flexible (no required adjacency).
IMPRISONMENT_PATTERNS = [
    # EN
    r"\b(in|behind)\s+(prison|jail|bars)\b",
    r"\bincarcerat(ed|ion)\b",
    r"\b(serving|served|doing)\s+(a\s+)?(sentence|time|life\s+sentence)\b",
    r"\b(convicted|sentenced)\s+(of|for)\b",
    r"\b(get(s|ting)?|being|to\s+be)\s+(released|let\s+out|out\s+of\s+(prison|jail))\b",
    r"\bprison\s+pen[-\s]?pal\b",
    r"\b(life|prison)\s+sentence\b",
    # RU: глаголы заключения / отбывания / освобождения — без жёсткой структуры
    r"\bсид(ит|ел|ела|им|ят)\b",
    r"\bотбыва(ет|ет\s+срок|л|ла|ют|ли)\b",
    r"\bв\s+(тюрьм\w+|колони\w+|сизо|зон\w+|местах\s+лишения\s+свобод\w+)\b",
    r"\bосужд(ён|ен|ена|ены|ённый|енный|енная)\b",
    r"\b(скоро\s+)?(выход(ит|ил|ила)|выйд(ет|у|ут)|освобожда(ется|лся|лась|ются)|освобод(ится|ился|илась|ятся))\s+(из\s+(тюрьм\w+|колони\w+|сизо|зон\w+)|на\s+свобод\w+)\b",
    r"\bна\s+свобод\w+\b",
    r"\bпожизненн\w+\s+(срок|заключени\w+)\b",
]

# Serious violent crime mentions — independent signal.
SERIOUS_CRIME_PATTERNS = [
    # EN
    r"\b(murder(ed|er|ers)?|killing|killed|homicide|killer)\b",
    r"\brape(d|r|s|rs)?\b",
    r"\bsexual\s+(assault|violence|abuse|offen[cs]e)\b",
    r"\b(violent\s+(crime|offender|offense|offence|crimes)|domestic\s+violence|manslaughter)\b",
    # RU
    r"\bубийств\w+\b",
    r"\bубил(а|и|и\s+\w+)?\b",
    r"\bубит\w+\b",
    r"\bубийц\w+\b",
    r"\bизнасилов(ал|ала|али|ан|ана|аны|ание|ания)\b",
    r"\bизнасилован\w+\b",
    r"\bнасильник\w+\b",
    r"\b(совершил|совершила|совершили)\s+\w*\s*(убийств\w+|изнасилован\w+|насил\w+|преступлен\w+)\b",
    r"\bтяжк\w+\s+(преступлен\w+|насил\w+)\b",
    r"\bнасильственн\w+\s+преступлен\w+\b",
]

# Strong amplifier: the criminal already knows where the user lives.
ADDRESS_KNOWLEDGE_PATTERNS = [
    # EN
    r"\b(he|she|they)\s+(already\s+)?knows?\s+(my\s+)?(address|where\s+i\s+live|where\s+my\s+(home|house)\s+is|my\s+home\s+address)\b",
    r"\b(he|she|they)\s+(has|have)\s+my\s+(address|home\s+address)\b",
    r"\bknows?\s+(my\s+address|where\s+i\s+live|where\s+my\s+(home|house)\s+is)\b",
    # RU
    r"\b(он|она|они)\s+(уже\s+)?знает\s+(мой\s+адрес|где\s+я\s+живу|где\s+я|где\s+мой\s+дом|где\s+(находится\s+)?мой\s+(дом|адрес))\b",
    r"\b(он|она|они)\s+знают?\s+(мой\s+адрес|где\s+я\s+живу)\b",
    # Free-form: "и знает мой адрес", "уже знает мой адрес" — no person-prefix required
    r"\bзнает\s+(мой\s+адрес|где\s+я\s+живу|где\s+мой\s+дом)\b",
    r"\bзнают\s+(мой\s+адрес|где\s+я\s+живу)\b",
    r"\bу\s+(него|неё|нее|них)\s+(есть\s+)?мой\s+адрес\b",
    r"\bему\s+известен\s+мой\s+(адрес|дом)\b",
]

# Discourse markers that downgrade signals — the user is talking about media, not their own life.
MEDIA_CONTEXT_PATTERNS = [
    # EN
    r"\b(in|on)\s+(a|the|that)?\s*(movie|film|book|series|tv\s+show|show|news|documentary|article|story|novel)\b",
    r"\b(watching|watched|read|reading)\s+(a|the|that)?\s*(movie|film|book|series|news|documentary|article|story|novel)\b",
    # RU
    r"\b(в|на)\s+(фильме|кино|книге|сериале|передаче|новостях|документалке|статье|романе|рассказе)\b",
    r"\b(смотр(ю|ел|ела|ела\s+\w+)|читал(а)?|чита(ю|ла))\s+(фильм|кино|книгу|сериал|передачу|новости|документалку|статью|роман|рассказ)\w*\b",
]

ROMANTIC_INVOLVEMENT_PATTERNS = [
    # EN
    r"\b(my|our)\s+(boyfriend|girlfriend|partner|husband|wife|fiance|fiancé|fiancee|fiancée|man|woman)\b",
    r"\b(i\s+(am|'m)\s+(dating|seeing|with))\b",
    r"\b(i\s+(love|adore))\s+him\b",
    r"\b(i\s+(love|adore))\s+her\b",
    r"\b(we\s+are|we're)\s+(together|dating|in\s+a\s+relationship)\b",
    r"\b(i\s+want|i\s+would\s+like|i'd\s+like|i\s+plan)\s+to\s+(continue|keep|stay|build|start)\s+(talking|writing|chatting|texting|a\s+relationship|things|seeing\s+him|seeing\s+her|with\s+him|with\s+her)\b",
    r"\b(i\s+want|i\s+would\s+like|i'd\s+like|i\s+plan)\s+to\s+(invite|bring|let)\s+(him|her|them)\s+(into|to|in)\b",
    r"\b(i\s+(write|chat|text|talk|correspond)\s+(with|to)\s+him)\b",
    r"\b(i\s+(write|chat|text|talk|correspond)\s+(with|to)\s+her)\b",
    r"\b(pen[-\s]?pal|prison\s+pen[-\s]?pal)\b",
    r"\bour\s+(letters|correspondence|relationship)\b",
    # RU
    r"\b(мой|моя|мои)\s+(парень|девушка|партнер|партнёр|муж|жена|жених|невеста|избранник|избранница|мужчина|любимый|любимая)\b",
    r"\b(я\s+(встречаюсь|встречаемся|вместе)\s+с\s+ним)\b",
    r"\b(я\s+(встречаюсь|встречаемся|вместе)\s+с\s+ней)\b",
    r"\b(я\s+(люблю|обожаю)\s+(его|её|ее))\b",
    r"\b(мы\s+(вместе|встречаемся|пара|в\s+отношениях))\b",
    r"\b(я\s+хочу|хочу|мне\s+хочется|планирую)\s+(продолжать|продолжить|сохранить|строить|начать)\s+(переписку|общение|отношения|общаться|переписываться|с\s+ним|с\s+ней|быть\s+с\s+ним|быть\s+с\s+ней)\b",
    r"\b(я\s+хочу|хочу|мне\s+хочется|планирую)\s+(пригласить|позвать|привести|впустить)\s+(его|её|ее|их)\b",
    r"\b(я\s+(переписываюсь|общаюсь|пишу|разговариваю)\s+с\s+(ним|ней))\b",
    r"\b(переписка|переписку|переписки)\s+с\s+(ним|ней)\b",
    r"\b(наш\w*|эт\w+)\s+(переписк\w+|общени\w+|письм\w+|отношени\w+)\b",
    r"\b(сближаться|сблизиться)\s+с\s+(ним|ней|ними)\b",
    r"\b(хочу|хочется)\s+быть\s+с\s+(ним|ней)\b",
]

MINIMIZATION_PATTERNS = [
    # EN
    r"\b(i\s+am|i'm|im)\s+not\s+afraid\b",
    r"\b(i\s+(trust|believe\s+in))\s+him\b",
    r"\b(i\s+(trust|believe\s+in))\s+her\b",
    r"\b(he|she)\s+(has\s+)?(repented|changed|is\s+a\s+changed\s+(man|woman|person)|deserves\s+a\s+second\s+chance)\b",
    r"\b(my|the)\s+(only\s+)?chance\s+(for|at|of)\s+(happiness|love|family)\b",
    r"\b(he|she)\s+(is\s+)?(my)\s+chance\b",
    r"\b(he|she)\s+is\s+(actually\s+)?(a\s+)?(good|kind|gentle|loving)\s+(man|woman|person|guy|soul)\b",
    r"\b(everyone\s+deserves|deserves)\s+(a\s+)?second\s+chance\b",
    r"\bi\s+feel\s+safe\s+with\s+(him|her)\b",
    # RU: «не страшно» / «не боюсь» — допускаем разные формы
    r"\bмне\s+не\s+страшно\b",
    r"\bне\s+страшно\b",
    r"\bя\s+не\s+бо(юсь|ялась|ялся)\b",
    r"\bне\s+бо(юсь|ялась|ялся)\s+(его|её|ее|их)\b",
    # «уверена / уверен» — расширяем форму
    r"\bя\s+(уверена|уверен)\s+в\s+(нём|нем|ней|этом\s+(человеке|мужчине)|этой\s+женщине)\b",
    r"\bя\s+(уверена|уверен),?\s+что\s+он\b",
    r"\bя\s+(уверена|уверен),?\s+что\s+она\b",
    r"\b(я\s+ему|я\s+ей)\s+верю\b",
    r"\bя\s+верю\s+в\s+(него|неё|нее)\b",
    # «раскаялся / изменился»
    r"\b(он|она)\s+(раскаялся|раскаялась|раскаивается|изменился|изменилась|стал\s+другим|стала\s+другой)\b",
    # «мой шанс / шанс на счастье»
    r"\b(это\s+)?(мой|её|единственный)\s+шанс\s+(на\s+(счастье|любовь|семью)|быть\s+счастлив\w+)\b",
    r"\b(он|она)\s+(мой|моя)\s+шанс\b",
    r"\b(мой|единственный)\s+шанс\s+быть\s+(счастлив\w+)\b",
    # «он хороший человек»
    r"\b(он|она)\s+(на\s+самом\s+деле\s+)?(хороший|добрый|нежный|любящий)\s+(человек|парень|мужчина|женщина|душа)\b",
    r"\b(каждый\s+заслуживает|заслуживает)\s+(второй\s+|еще\s+один\s+|ещё\s+один\s+)?шанс\b",
    r"\bтолько\s+он\s+меня\s+(понимает|любит)\b",
]

CHILDREN_PRESENT_PATTERNS = [
    # EN
    r"\b(my|our)\s+(child|children|kid|kids|son|daughter|daughters|sons|baby|babies)\b",
    r"\b(kids|children)\s+(at\s+home|in\s+the\s+house|around|with\s+me)\b",
    r"\bi\s+have\s+(a\s+)?(child|children|kid|kids|son|daughter|baby|two\s+kids|three\s+kids|two\s+children|three\s+children)\b",
    # RU: расширяем числительные ("двое детей", "трое детей") и формы
    r"\b(мой|моя|мои|наш|наша|наши)\s+(ребенок|ребёнок|дети|сын|дочь|дочка|малыш|младенец|сыновья|дочери)\b",
    r"\b(дома|со\s+мной|рядом|в\s+доме|в\s+квартире|в\s+семье)\s+(есть\s+)?(дети|ребенок|ребёнок|малыш|малыши|двое\s+детей|трое\s+детей|двое|трое|маленьк\w+\s+ребенок|маленьк\w+\s+ребёнок)\b",
    r"\bу\s+(меня|нас)\s+(дома\s+)?(есть\s+)?(дети|ребенок|ребёнок|сын|дочь|дочка|малыш|двое\s+(детей|сыновей|дочерей|малышей)|трое\s+(детей|сыновей|дочерей|малышей)|двое|трое)\b",
    r"\bу\s+(меня|нас)\s+маленьк\w+\s+(ребенок|ребёнок|дети)\b",
]


def check_crisis(message):
    """
    Проверяет, есть ли в сообщении признаки кризиса.
    Возвращает ('high', reason) или ('none', None)
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"CRISIS DETECTED: {keyword}")
            return "high", keyword

    return "none", None


def check_abuse_violence(message):
    """
    Проверяет, есть ли признаки насилия, угроз, coercive control,
    страха за безопасность и других red flags.
    Возвращает ('high', reason) или ('none', None)
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for pattern, reason in ABUSE_VIOLENCE_PATTERNS:
        if re.search(pattern, message_lower):
            logger.warning(f"ABUSE/VIOLENCE SAFETY CASE DETECTED: {reason}")
            return "high", reason

    return "none", None


def check_fraud_financial_pressure(message):
    """
    Проверяет признаки мошенничества, шантажа, финансового давления:
    просьбы взять кредит/занять/перевести деньги, требования кодов/документов,
    шантаж, вымогательство, scam, давление через тюрьму.
    Возвращает ('high', reason) или ('none', None).
    """
    if not message:
        return "none", None

    message_lower = message.lower()

    for pattern, reason in FRAUD_FINANCIAL_PATTERNS:
        if re.search(pattern, message_lower):
            logger.warning(f"FRAUD/FINANCIAL PRESSURE SAFETY CASE DETECTED: {reason}")
            return "high", reason

    return "none", None


def _any_match(patterns, text):
    return any(re.search(p, text) for p in patterns)


def check_dangerous_partner_or_criminal_risk(message):
    """
    Проверяет, описывает ли пользователь романтическую вовлечённость
    в человека с серьёзным криминальным контекстом (тюрьма / отбывает срок
    и/или насильственное преступление: убийство, изнасилование, насилие),
    либо минимизирует риск, хочет сближаться, упоминает уязвимых детей
    рядом, либо что криминальный человек уже знает её адрес.

    Структура:
    - imprisonment / serious_crime / address_knowledge — независимые сигналы криминального контекста.
    - При media-context (фильм/книга/новости) сигналы downgrade'ятся, если они единственные.
    - Trigger: criminal_context AND (romantic OR minimization OR children OR address).
      Если найдено address_knowledge при наличии любого imprisonment/crime сигнала — это
      самостоятельный triggering сигнал безопасности.

    Возвращает ('high', reason) или ('none', None).
    """
    if not message:
        return "none", None

    msg = message.lower()

    has_imprisonment = _any_match(IMPRISONMENT_PATTERNS, msg)
    has_serious_crime = _any_match(SERIOUS_CRIME_PATTERNS, msg)
    has_address = _any_match(ADDRESS_KNOWLEDGE_PATTERNS, msg)
    has_media_context = _any_match(MEDIA_CONTEXT_PATTERNS, msg)

    has_criminal_context = has_imprisonment or has_serious_crime or has_address
    if not has_criminal_context:
        return "none", None

    has_romantic = _any_match(ROMANTIC_INVOLVEMENT_PATTERNS, msg)
    has_minimization = _any_match(MINIMIZATION_PATTERNS, msg)
    has_children = _any_match(CHILDREN_PRESENT_PATTERNS, msg)

    # Media context guard: if user is talking about a movie/book/news AND there is
    # no clear personal-life signal (romantic / minimization / children / address),
    # do not trigger. This protects "я смотрела фильм про человека в тюрьме" cases.
    has_personal_signal = (
        has_romantic or has_minimization or has_children or has_address
    )
    if has_media_context and not has_personal_signal:
        return "none", None

    if not has_personal_signal:
        return "none", None

    signals = []
    if has_imprisonment:
        signals.append("imprisonment")
    if has_serious_crime:
        signals.append("serious_crime")
    if has_address:
        signals.append("address_knowledge")
    if has_romantic:
        signals.append("romantic_involvement")
    if has_minimization:
        signals.append("minimization")
    if has_children:
        signals.append("children_present")
    reason = "+".join(signals)
    logger.warning(
        f"DANGEROUS PARTNER / CRIMINAL RISK SAFETY CASE DETECTED: {reason}"
    )
    return "high", reason


def get_crisis_response(language="en"):
    """Возвращает кризисный ответ"""
    from prompts import get_crisis_message, normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        suggested_technique = "Экстренная поддержка"
        technique_description = (
            "Сразу обратись к живому специалисту или в экстренные службы."
        )
    else:
        suggested_technique = "Emergency support"
        technique_description = "Contact a live professional, crisis line, or emergency services immediately."

    return {
        "message": get_crisis_message(current_language),
        "detected_state": "crisis",
        "suggested_technique": suggested_technique,
        "technique_description": technique_description,
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "crisis",
        "show_technique": False,
        "needs_specialist_support": True,
    }


def get_abuse_violence_response(language="en"):
    """Возвращает safety-ответ при признаках насилия/угроз/абьюза."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Спасибо, что поделился этим. То, что ты описываешь, похоже на серьезный red flag и может быть опасной ситуацией, "
                "а не обычной ссорой. Твоя безопасность сейчас важнее всего. "
                "Пожалуйста, обратись за поддержкой к человеку, которому доверяешь, психологу или кризисной службе. "
                "Если есть риск немедленной опасности, сразу звони в экстренные службы."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "План безопасности",
            "technique_description": (
                "Определи безопасное место, подготовь контакты экстренной помощи и человека, которому можно написать или позвонить прямо сейчас."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "safety_category": "abuse_violence",
            "show_technique": False,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "Thank you for sharing this. What you describe is a serious safety red flag and may be dangerous, not a normal relationship conflict. "
            "Your safety comes first. Please reach out to a trusted person, a mental health professional, or a crisis support service. "
            "If there is immediate danger, contact emergency services right now."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Safety first plan",
        "technique_description": (
            "Identify a safe place, prepare emergency contacts, and contact a trusted person or crisis service now."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "abuse_violence",
        "show_technique": False,
        "needs_specialist_support": True,
    }


def check_history_for_safety_flags(conversation_history):
    """
    Сканирует conversation_history на наличие прошлых red flags.
    Возвращает True, если хотя бы одно user-сообщение содержало
    crisis, abuse/violence, fraud/financial-pressure или
    dangerous-partner / criminal-risk триггер.
    """
    if not conversation_history:
        return False

    for entry in conversation_history:
        if entry.get("role") != "user":
            continue
        content = entry.get("content", "")
        crisis_level, _ = check_crisis(content)
        if crisis_level == "high":
            return True
        abuse_level, _ = check_abuse_violence(content)
        if abuse_level == "high":
            return True
        fraud_level, _ = check_fraud_financial_pressure(content)
        if fraud_level == "high":
            return True
        dangerous_level, _ = check_dangerous_partner_or_criminal_risk(content)
        if dangerous_level == "high":
            return True

    return False


def get_fraud_financial_response(language="en", reason=None):
    """Safety-ответ при fraud / blackmail / financial pressure."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Спасибо, что поделился этим. То, что ты описываешь, похоже на серьезный red flag: "
                "это может быть давление, шантаж, вымогательство, мошенничество или финансовая манипуляция, "
                "а не обычный конфликт в отношениях. Сделай паузу и не принимай решений под давлением. "
                "Не переводи деньги, не бери кредит, не передавай документы, пароли, коды из СМС или банковские данные. "
                "Обратись к человеку, которому доверяешь, в банк, в службу поддержки или в полицию, "
                "если ситуация выглядит опасной."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "Пауза и защита",
            "technique_description": (
                "Не принимай решений сейчас. Не переводи деньги и не передавай данные. "
                "Свяжись с доверенным человеком, банком или службой поддержки."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "safety_category": "fraud_blackmail_financial_pressure",
            "show_technique": False,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "Thank you for sharing this. What you describe sounds like a serious red flag: "
            "this can be pressure, blackmail, extortion, a scam, or financial manipulation, "
            "not a normal relationship conflict. Pause and do not make decisions under pressure. "
            "Do not transfer money, do not take a loan, and do not share documents, passwords, "
            "verification codes, or banking data. Reach out to a trusted person, your bank, "
            "platform support, or the police if the situation looks dangerous."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Pause and protect",
        "technique_description": (
            "Do not decide now. Do not transfer money or share personal data. "
            "Contact a trusted person, your bank, or a support service."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "fraud_blackmail_financial_pressure",
        "show_technique": False,
        "needs_specialist_support": True,
    }


def get_dangerous_partner_response(language="en", reason=None):
    """Safety-ответ при романтической вовлечённости с человеком, имеющим
    серьёзный криминальный контекст (тюрьма за насильственные преступления,
    убийство, изнасилование), и/или при минимизации риска, желании сближаться,
    наличии уязвимых детей рядом."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Спасибо, что поделился этим. То, что ты описываешь, — серьёзный red flag, "
                "а не обычная история отношений. Сближение с человеком, у которого в прошлом "
                "тяжёлые насильственные преступления или который сейчас отбывает срок за такие "
                "преступления, несёт реальный риск для тебя и людей рядом, особенно для детей. "
                "Сейчас важно не принимать решений в одиночку и под влиянием чувств. "
                "Не приглашай этого человека ближе к себе или к детям без профессиональной "
                "оценки риска. Обратись к психологу или специалисту, который работает с "
                "domestic violence / risk assessment, и обсуди ситуацию с доверенным человеком."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "Профессиональная оценка риска",
            "technique_description": (
                "Не решай в одиночку и не сближай этого человека с собой или детьми. "
                "Запиши факты, обратись к психологу или специалисту по оценке риска, "
                "поговори с доверенным человеком."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "safety_category": "dangerous_partner_or_criminal_risk",
            "show_technique": False,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "Thank you for sharing this. What you describe is a serious red flag, not a normal "
            "relationship story. Getting closer to a person with a history of serious violent "
            "crimes — or someone currently serving time for such crimes — carries a real risk "
            "to you and to the people around you, especially children. Please do not make this "
            "decision alone or under the weight of feelings. Do not bring this person closer to "
            "you or to your children without a professional risk assessment. Talk to a "
            "psychologist or a specialist who works with domestic violence and risk assessment, "
            "and share the situation with a trusted person."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Professional risk assessment",
        "technique_description": (
            "Do not decide alone and do not bring this person closer to you or your children. "
            "Write down the facts, contact a psychologist or risk-assessment specialist, "
            "and talk to a trusted person."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "dangerous_partner_or_criminal_risk",
        "show_technique": False,
        "needs_specialist_support": True,
    }


def get_safety_mode_followup_response(language="en"):
    """Возвращает ответ, когда safety-mode уже активен для текущей сессии."""
    from prompts import normalize_language

    current_language = normalize_language(language)

    if current_language == "ru":
        return {
            "message": (
                "Сейчас важно не рассматривать это как обычный конфликт. "
                "Похоже, вопрос связан с безопасностью. "
                "Давай сфокусируемся на твоей защите и поддержке: обратись к человеку, которому доверяешь, "
                "к психологу или в кризисную службу. Если есть риск немедленной опасности, звони в экстренные службы."
            ),
            "detected_state": "safety_risk",
            "suggested_technique": "Поддержка и безопасность",
            "technique_description": (
                "Сделай один безопасный шаг прямо сейчас: свяжись с trusted person, специалистом или службой поддержки."
            ),
            "risk_level": "high",
            "safety_mode": True,
            "safety_category": "safety_followup",
            "show_technique": False,
            "needs_specialist_support": True,
        }

    return {
        "message": (
            "This should not be treated as a normal relationship conflict. "
            "It still looks like a safety-focused situation. "
            "Let us keep the focus on your protection and support: contact a trusted person, a mental health professional, "
            "or a crisis support service. If there is immediate danger, call emergency services now."
        ),
        "detected_state": "safety_risk",
        "suggested_technique": "Safety and support step",
        "technique_description": (
            "Take one concrete safety step now: contact a trusted person, a professional, or a support service."
        ),
        "risk_level": "high",
        "safety_mode": True,
        "safety_category": "safety_followup",
        "show_technique": False,
        "needs_specialist_support": True,
    }
