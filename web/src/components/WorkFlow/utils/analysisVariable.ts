/*
 * @LastEditors: biz
 */

export default function parseText(
    text: string,
): { identifier: string; ioType: string; fieldName: string }[] {
    const pattern = /<<([0-9a-fA-F\-]+)\.(inputs|outputs)\.([^>]+)>>/g;
    const results: { identifier: string; ioType: string; fieldName: string }[] = [];

    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
        const identifier = match[1];
        const ioType = match[2];
        const fieldName = match[3];
        results.push({ identifier, ioType, fieldName });
    }

    return results;
}
