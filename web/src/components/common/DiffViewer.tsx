import classNames from 'classnames';
import React, { useMemo } from 'react';

type DiffType = 'equal' | 'add' | 'remove';

interface DiffRow {
    type: DiffType;
    oldLine?: string;
    newLine?: string;
    oldNumber?: number;
    newNumber?: number;
}

interface DiffViewerProps {
    original?: string;
    modified?: string;
    className?: string;
}

const buildDiffRows = (original: string, modified: string): DiffRow[] => {
    const left = original.split('\n');
    const right = modified.split('\n');
    const m = left.length;
    const n = right.length;
    const dp: number[][] = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));

    for (let i = m - 1; i >= 0; i -= 1) {
        for (let j = n - 1; j >= 0; j -= 1) {
            if (left[i] === right[j]) {
                dp[i][j] = dp[i + 1][j + 1] + 1;
            } else {
                dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
            }
        }
    }

    const rows: DiffRow[] = [];
    let i = 0;
    let j = 0;

    while (i < m && j < n) {
        if (left[i] === right[j]) {
            rows.push({
                type: 'equal',
                oldLine: left[i],
                newLine: right[j],
                oldNumber: i + 1,
                newNumber: j + 1,
            });
            i += 1;
            j += 1;
        } else if (dp[i + 1][j] >= dp[i][j + 1]) {
            rows.push({
                type: 'remove',
                oldLine: left[i],
                oldNumber: i + 1,
            });
            i += 1;
        } else {
            rows.push({
                type: 'add',
                newLine: right[j],
                newNumber: j + 1,
            });
            j += 1;
        }
    }

    while (i < m) {
        rows.push({
            type: 'remove',
            oldLine: left[i],
            oldNumber: i + 1,
        });
        i += 1;
    }

    while (j < n) {
        rows.push({
            type: 'add',
            newLine: right[j],
            newNumber: j + 1,
        });
        j += 1;
    }

    return rows;
};

const DiffViewer: React.FC<DiffViewerProps> = ({ original = '', modified = '', className }) => {
    const rows = useMemo(() => buildDiffRows(original, modified), [original, modified]);

    return (
        <div className={classNames('rounded-lg border border-gray-200 overflow-hidden text-xs font-mono', className)}>
            <div className="grid grid-cols-[64px_1fr_64px_1fr] bg-gray-100 text-gray-500 uppercase tracking-wide">
                <div className="px-2 py-1 text-right">Old</div>
                <div className="px-2 py-1">Content</div>
                <div className="px-2 py-1 text-right">New</div>
                <div className="px-2 py-1">Content</div>
            </div>
            <div>
                {rows.map((row, index) => {
                    const rowClass =
                        row.type === 'add'
                            ? 'bg-green-50'
                            : row.type === 'remove'
                            ? 'bg-red-50'
                            : 'bg-white';

                    return (
                        <div
                            key={`${row.type}-${index}-${row.oldNumber ?? '-'}-${row.newNumber ?? '-'}`}
                            className={classNames(
                                'grid grid-cols-[64px_1fr_64px_1fr] border-t border-gray-100',
                                rowClass,
                            )}
                        >
                            <div className="px-2 py-1 text-right text-gray-500">
                                {row.oldNumber ?? ''}
                            </div>
                            <div
                                className={classNames(
                                    'px-2 py-1 whitespace-pre-wrap break-words',
                                    row.type === 'remove' ? 'text-red-600' : 'text-gray-800',
                                )}
                            >
                                {row.oldLine ?? ''}
                            </div>
                            <div className="px-2 py-1 text-right text-gray-500">
                                {row.newNumber ?? ''}
                            </div>
                            <div
                                className={classNames(
                                    'px-2 py-1 whitespace-pre-wrap break-words',
                                    row.type === 'add' ? 'text-green-600' : 'text-gray-800',
                                )}
                            >
                                {row.newLine ?? ''}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default DiffViewer;
